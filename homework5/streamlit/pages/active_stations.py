import streamlit as st
import pydeck as pdk
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from api_client import get_api_client
from db_client import get_db_client
from auth import get_auth_cookie

st.set_page_config(page_title="Active Stations", layout="wide")

# Get clients
api = get_api_client()
db = get_db_client()

# Initialize session state for user
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

# Check for existing session from cookie if not already logged in
if not st.session_state.logged_in:
    auth_data = get_auth_cookie()
    if auth_data:
        user_data = db.get_user_by_session(auth_data['session_token'])
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user = user_data

st.title("📍 Active Stations Map")

# Sidebar user info
with st.sidebar:
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.user.get('callsign', 'User')}")
        if st.session_state.user.get('name'):
            st.caption(f"{st.session_state.user['name']}")
        if st.session_state.user.get('grid_square'):
            st.caption(f"📍 {st.session_state.user['grid_square']}")
        st.divider()
    else:
        st.info("Login to customize settings")
        st.divider()

st.markdown("""
Geographic visualization of active DX stations plotted by their Maidenhead grid square locations.
""")

# Controls
col1, col2 = st.columns(2)

with col1:
    band = st.selectbox("Band", options=["All Bands", "40m", "30m", "20m", "17m", "15m", "12m", "10m"], index=0)

with col2:
    hours = st.selectbox("Time Window (hours)", options=[1, 2, 4, 8, 12, 24], index=2)

# Debug info
st.caption(f"Current filters: Band={band}, Hours={hours}")

# Load callsign country lookup table
@st.cache_data
def load_callsign_countries():
    """Load callsign prefix to country/lat/lon mapping"""
    import json
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'callsign_countries.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['prefixes']

# Function to get coordinates from callsign prefix
def get_coordinates_from_callsign(callsign, prefix_lookup):
    """
    Extract approximate coordinates from callsign using country prefix lookup.
    Falls back to grid square conversion if available.
    """
    if not callsign:
        return None, None
    
    callsign = callsign.upper().strip()
    
    # Try progressively longer prefixes (up to 4 characters for special prefixes like KH5K)
    for length in [4, 3, 2, 1]:
        if len(callsign) >= length:
            prefix = callsign[:length]
            if prefix in prefix_lookup:
                return prefix_lookup[prefix]['lat'], prefix_lookup[prefix]['lon']
    
    # Handle special US callsigns (K/N/W/A + digit)
    if len(callsign) >= 2:
        first_char = callsign[0]
        if first_char in ['K', 'N', 'W', 'A']:
            # Find first digit
            for i, char in enumerate(callsign):
                if char.isdigit():
                    # US callsign format: prefix + digit + suffix
                    # Just use 'K' as generic US prefix
                    if 'K' in prefix_lookup:
                        return prefix_lookup['K']['lat'], prefix_lookup['K']['lon']
                    break
    
    return None, None

# Function to convert Maidenhead grid to lat/lon (fallback)
def maidenhead_to_latlon(grid):
    """Convert 6-character Maidenhead grid square to latitude/longitude"""
    if not grid or len(grid) < 4:
        return None, None
    try:
        # Pad grid to 6 characters if needed
        grid = grid.ljust(6, 'A')
        lon = (ord(grid[0].upper()) - ord('A')) * 20 - 180
        lat = (ord(grid[1].upper()) - ord('A')) * 10 - 90
        lon += int(grid[2]) * 2
        lat += int(grid[3])
        if len(grid) >= 6:
            lon += (ord(grid[4].lower()) - ord('a')) * (2 / 24)
            lat += (ord(grid[5].lower()) - ord('a')) * (1 / 24)
        return lat, lon
    except:
        return None, None

# Function to fetch data from API
def fetch_active_stations(band_filter, hours_filter):
    """Fetch active stations from API with filters"""
    import requests
    import socket
    try:
        # Force IPv4 connection
        old_getaddrinfo = socket.getaddrinfo
        
        def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return old_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        
        socket.getaddrinfo = getaddrinfo_ipv4_only
        
        try:
            # Build URL - fetch all data and filter client-side for reliability
            url = f"http://api.jxqz.org:8080/api/spots/recent?limit=1000"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            spots = data.get('spots', data) if isinstance(data, dict) else data
            
            if not spots:
                return []
            
            # Apply band filter client-side
            if band_filter != "All Bands":
                spots = [s for s in spots if s.get('band') == band_filter]
            
            # Apply time filter
            if hours_filter:
                cutoff_time = datetime.now() - timedelta(hours=hours_filter)
                filtered_spots = []
                for spot in spots:
                    try:
                        # Parse timestamp - adjust format based on your API response
                        spot_time = datetime.fromisoformat(spot.get('timestamp', '').replace('Z', '+00:00'))
                        if spot_time >= cutoff_time:
                            filtered_spots.append(spot)
                    except:
                        # If timestamp parsing fails, include the spot
                        filtered_spots.append(spot)
                spots = filtered_spots
            
            return spots
            
        finally:
            socket.getaddrinfo = old_getaddrinfo
            
    except Exception as e:
        st.error(f"API request failed: {e}")
        st.info("Tip: Check that API is accessible and not blocking IPv6")
        return []

# Fetch data from API
with st.spinner("Fetching active stations..."):
    spots = fetch_active_stations(band, hours)

if spots:
    df = pd.DataFrame(spots)
    
    # Convert frequency from kHz to MHz with 3 decimal places for display
    if 'frequency' in df.columns:
        df['frequency_mhz'] = df['frequency'].apply(lambda x: f"{float(x)/1000:.3f}" if pd.notna(x) else "")
    
    # Load callsign prefix lookup
    prefix_lookup = load_callsign_countries()
    
    # Get coordinates from callsign prefix (primary method)
    df[['lat', 'lon']] = df['dx_call'].apply(
        lambda x: pd.Series(get_coordinates_from_callsign(x, prefix_lookup))
    )
    
    # Fallback to grid square if callsign lookup failed and grid is available
    if 'grid_square' in df.columns:
        missing_coords = df['lat'].isna()
        if missing_coords.any():
            df.loc[missing_coords, ['lat', 'lon']] = df.loc[missing_coords, 'grid_square'].apply(
                lambda x: pd.Series(maidenhead_to_latlon(x))
            )
    
    # Remove rows with no valid coordinates
    initial_count = len(df)
    df = df.dropna(subset=['lat', 'lon'])
    
    if len(df) < initial_count:
        st.info(f"Mapped {len(df)} of {initial_count} stations ({initial_count - len(df)} could not be located)")
    
    if not df.empty:
        # Aggregate spots by callsign - count occurrences and get first location
        callsign_agg = df.groupby('dx_call').agg({
            'lat': 'first',
            'lon': 'first',
            'frequency': 'first',
            'frequency_mhz': 'first',
            'band': 'first',
            'mode': 'first',
            'grid_square': 'first' if 'grid_square' in df.columns else lambda x: None
        }).reset_index()
        
        # Count spots per callsign
        callsign_agg['spot_count'] = df.groupby('dx_call').size().values
        
        # Scale radius based on spot count (base 30k, scale up with count)
        callsign_agg['radius'] = callsign_agg['spot_count'].apply(lambda x: 30000 + (x * 15000))
        
        st.success(f"Displaying {len(callsign_agg)} unique stations from {len(df)} total spots")
        
        # Create PyDeck scatterplot map
        layer = pdk.Layer(
            "ScatterplotLayer",
            callsign_agg,
            get_position=["lon", "lat"],
            get_color=[200, 30, 0, 160],
            get_radius="radius",
            pickable=True,
        )
        
        view_state = pdk.ViewState(
            latitude=callsign_agg['lat'].mean(),
            longitude=callsign_agg['lon'].mean(),
            zoom=2,
            pitch=0,
        )
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{dx_call}\n{frequency_mhz} MHz\n{spot_count} spots"},
            map_style='light',
        )
        
        st.pydeck_chart(deck, width='stretch')
        
        # Statistics
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Spots", len(df))
        
        with col2:
            st.metric("Unique Callsigns", callsign_agg['dx_call'].nunique())
        
        with col3:
            if 'band' in df.columns:
                st.metric("Active Bands", df['band'].nunique())
        
        with col4:
            if 'mode' in df.columns and df['mode'].notna().any():
                st.metric("Modes", df['mode'].nunique())
        
        # Show data table
        with st.expander("📊 View Station Data"):
            display_columns = ['dx_call', 'spot_count', 'frequency', 'band', 'mode', 'grid_square', 'lat', 'lon']
            available_columns = [col for col in display_columns if col in callsign_agg.columns]
            st.dataframe(callsign_agg[available_columns].sort_values('spot_count', ascending=False), 
                        width='stretch')
    else:
        st.warning("No stations could be located on the map.")
        st.info("Stations are located by callsign prefix or grid square when available.")
else:
    st.warning("No data available. Check that the API is running and accessible.")
    st.info(f"API URL: {api.base_url}")

st.divider()

st.info("💡 **Tip**: Hover over dots to see callsign, frequency, and spot count. Larger circles indicate more spots for that station.")
