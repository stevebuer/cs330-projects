import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pydeck as pdk
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import custom clients
from api_client import get_api_client
from db_client import get_db_client

st.set_page_config(page_title="Great Circle Paths", layout="wide")

# Initialize session state for user
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

# Get clients
api = get_api_client()
db = get_db_client()

# Callsign prefix to coordinates mapping
CALLSIGN_REGIONS = {
    # US Callsign areas
    'K1': {'lat': 42.3601, 'lon': -71.0589, 'name': 'New England'},
    'K2': {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York/New Jersey'},
    'K3': {'lat': 39.9526, 'lon': -75.1652, 'name': 'Mid-Atlantic'},
    'K4': {'lat': 33.7490, 'lon': -84.3880, 'name': 'Southeast'},
    'K5': {'lat': 29.7604, 'lon': -95.3698, 'name': 'South Central'},
    'K6': {'lat': 34.0522, 'lon': -118.2437, 'name': 'California'},
    'K7': {'lat': 47.6062, 'lon': -122.3321, 'name': 'Pacific Northwest'},
    'K8': {'lat': 41.4993, 'lon': -81.6944, 'name': 'Great Lakes'},
    'K9': {'lat': 41.8781, 'lon': -87.6298, 'name': 'Midwest'},
    'K0': {'lat': 39.0997, 'lon': -94.5786, 'name': 'Central Plains'},
    # European prefixes
    'G': {'lat': 51.5074, 'lon': -0.1278, 'name': 'England'},
    'F': {'lat': 48.8566, 'lon': 2.3522, 'name': 'France'},
    'DL': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Germany'},
    'I': {'lat': 41.9028, 'lon': 12.4964, 'name': 'Italy'},
    'EA': {'lat': 40.4168, 'lon': -3.7038, 'name': 'Spain'},
    'ON': {'lat': 50.8503, 'lon': 4.3517, 'name': 'Belgium'},
    'PA': {'lat': 52.3676, 'lon': 4.9041, 'name': 'Netherlands'},
    'OH': {'lat': 60.1699, 'lon': 24.9384, 'name': 'Finland'},
    'SM': {'lat': 59.3293, 'lon': 18.0686, 'name': 'Sweden'},
    'LA': {'lat': 59.9139, 'lon': 10.7522, 'name': 'Norway'},
    'HB': {'lat': 46.9480, 'lon': 7.4474, 'name': 'Switzerland'},
    'GM': {'lat': 55.9533, 'lon': -3.1883, 'name': 'Scotland'},
    'EI': {'lat': 53.3498, 'lon': -6.2603, 'name': 'Ireland'},
    'CT': {'lat': 38.7223, 'lon': -9.1393, 'name': 'Portugal'},
    'CN': {'lat': 33.5731, 'lon': -7.5898, 'name': 'Morocco'},
    # Other regions
    'VE': {'lat': 45.4215, 'lon': -75.6972, 'name': 'Canada'},
    'VA': {'lat': 43.6532, 'lon': -79.3832, 'name': 'Canada'},
    'JA': {'lat': 35.6762, 'lon': 139.6503, 'name': 'Japan'},
    'ZS': {'lat': -25.7461, 'lon': 28.1881, 'name': 'South Africa'},
    'VK': {'lat': -33.8688, 'lon': 151.2093, 'name': 'Australia'},
    'ZL': {'lat': -41.2865, 'lon': 174.7762, 'name': 'New Zealand'},
    'PY': {'lat': -23.5505, 'lon': -46.6333, 'name': 'Brazil'},
    'LU': {'lat': -34.6037, 'lon': -58.3816, 'name': 'Argentina'},
    'CE': {'lat': -33.4489, 'lon': -70.6693, 'name': 'Chile'},
    'XE': {'lat': 19.4326, 'lon': -99.1332, 'name': 'Mexico'},
    'KP4': {'lat': 18.2208, 'lon': -66.5901, 'name': 'Puerto Rico'},
    '9Y': {'lat': 10.6918, 'lon': -61.2225, 'name': 'Trinidad'},
    'IK': {'lat': 45.4642, 'lon': 9.1900, 'name': 'Italy'},
    'IZ': {'lat': 41.9028, 'lon': 12.4964, 'name': 'Italy'},
    'IW': {'lat': 41.9028, 'lon': 12.4964, 'name': 'Italy'},
    'DK': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Germany'},
}

def get_coordinates(callsign):
    """Extract approximate coordinates from callsign prefix."""
    if not callsign:
        return None
    
    # Try progressively shorter prefixes
    for length in [3, 2, 1]:
        prefix = callsign[:length].upper()
        if prefix in CALLSIGN_REGIONS:
            return CALLSIGN_REGIONS[prefix]
    
    # Handle US callsigns (N/W/K/A prefix with digit)
    first_char = callsign[0].upper()
    if first_char in ['N', 'W', 'K', 'A'] and len(callsign) > 1:
        # Try digit at position 1
        if callsign[1].isdigit():
            key = f'K{callsign[1]}'
            if key in CALLSIGN_REGIONS:
                return CALLSIGN_REGIONS[key]
        # Try digit at position 2 (for KE4, KF4, etc.)
        if len(callsign) > 2 and callsign[2].isdigit():
            key = f'K{callsign[2]}'
            if key in CALLSIGN_REGIONS:
                return CALLSIGN_REGIONS[key]
    
    return None

st.title("🌍 Great Circle Paths")

st.markdown("""
Interactive 3D visualization of great circle propagation paths using PyDeck.
Great circle paths represent the shortest distance between two points on Earth's surface.
""")

# Sidebar controls
with st.sidebar:
    # User info
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.user.get('callsign', 'User')}")
        if st.session_state.user.get('name'):
            st.caption(f"{st.session_state.user['name']}")
        if st.session_state.user.get('grid_square'):
            st.caption(f"📍 {st.session_state.user['grid_square']}")
        st.divider()
    else:
        st.info("👤 Not logged in")
        st.caption("Visit User Login page to personalize")
        st.divider()
    
    st.header("⚙️ Settings")
    
    st.subheader("Band Selection")
    show_10m_fm = st.checkbox("10m FM (29.6-29.7 MHz)", value=False)
    show_10m_ssb = st.checkbox("10m SSB (28.3-28.99 MHz)", value=False)
    show_12m = st.checkbox("12m SSB (24.89-24.99 MHz)", value=False)
    show_15m = st.checkbox("15m SSB (21.2-21.45 MHz)", value=False)
    show_17m = st.checkbox("17m SSB (18.11-18.168 MHz)", value=False)
    show_20m = st.checkbox("20m SSB (14.15-14.35 MHz)", value=True)
    show_30m = st.checkbox("30m CW/Digital (10.1-10.15 MHz)", value=False)
    show_40m = st.checkbox("40m SSB (7.125-7.3 MHz)", value=False)
    
    st.divider()
    
    st.subheader("Time Window")
    time_window = st.selectbox("Show spots from", 
                               options=["Last 1 hour", "Last 2 hours", "Last 4 hours", "Last 6 hours", "Last 12 hours", "Last 24 hours", "Today"],
                               index=1)
    
    st.divider()
    
    st.subheader("Display Options")
    map_style_option = st.selectbox("Map Style", ["Light", "Dark"])
    arc_width = st.slider("Arc Width", min_value=1, max_value=5, value=2)
    
    st.divider()
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

st.divider()

# Fetch data
with st.spinner("Fetching DX spots..."):
    try:
        # Determine time range in hours
        if time_window == "Today":
            # Calculate hours since midnight today
            now = datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            hours = int((now - midnight).total_seconds() / 3600) + 1
        elif time_window == "Last 24 hours":
            hours = 24
        elif time_window == "Last 12 hours":
            hours = 12
        elif time_window == "Last 6 hours":
            hours = 6
        elif time_window == "Last 4 hours":
            hours = 4
        elif time_window == "Last 2 hours":
            hours = 2
        else:  # Last 1 hour
            hours = 1
        
        # Define band parameters: (band_name, min_freq, max_freq, checkbox_state)
        band_filters = []
        if show_10m_fm:
            band_filters.append(('10m', 29600, 29700))
        if show_10m_ssb:
            band_filters.append(('10m', 28300, 28990))
        if show_12m:
            band_filters.append(('12m', 24890, 24990))
        if show_15m:
            band_filters.append(('15m', 21200, 21450))
        if show_17m:
            band_filters.append(('17m', 18110, 18168))
        if show_20m:
            band_filters.append(('20m', 14150, 14350))
        if show_30m:
            band_filters.append(('30m', 10100, 10150))
        if show_40m:
            band_filters.append(('40m', 7125, 7300))
        
        # Check if any bands are selected
        if not band_filters:
            st.info("📡 Please select at least one band from the sidebar to display propagation data.")
            st.stop()
        
        # Fetch spots for selected bands
        all_band_spots = []
        
        # Fetch spots for each selected band
        for band_name, min_freq, max_freq in band_filters:
            band_spots = api.get_spots(band=band_name, hours=hours, limit=1000)
            # Filter by frequency range for SSB/FM portions
            for spot in band_spots:
                try:
                    freq = float(spot['frequency'])
                    if min_freq <= freq <= max_freq:
                        all_band_spots.append(spot)
                except (ValueError, KeyError):
                    continue
        
        spots = all_band_spots
        
        # Check if we got any spots
        if not spots:
            st.warning("📭 No spots found for the selected bands and time period. Try selecting different bands or expanding the time window.")
            st.stop()
        
        # Process spots and create arc data
        arc_data = []
        for spot in spots:
            spotter_coords = get_coordinates(spot['spotter_call'])
            dx_coords = get_coordinates(spot['dx_call'])
            
            if spotter_coords and dx_coords:
                arc = {
                    'source_lat': spotter_coords['lat'],
                    'source_lon': spotter_coords['lon'],
                    'target_lat': dx_coords['lat'],
                    'target_lon': dx_coords['lon'],
                    'spotter': spot['spotter_call'],
                    'dx_station': spot['dx_call'],
                    'frequency': spot['frequency'],
                    'mode': spot.get('mode', 'N/A'),
                    'timestamp': spot['timestamp'],
                    'comment': spot.get('comment', ''),
                }
                arc_data.append(arc)
        
        if not arc_data:
            st.warning("No coordinates found for the selected spots. Check callsign coverage.")
            st.stop()
        
        df = pd.DataFrame(arc_data)
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Spots", len(spots))
        with col2:
            st.metric("Visualized Paths", len(df))
        with col3:
            st.metric("DX Stations", df['dx_station'].nunique())
        with col4:
            st.metric("Spotters", df['spotter'].nunique())
        
        st.divider()
        
        # Create PyDeck visualization
        st.subheader("🗺️ Interactive Great Circle Map")
        
        layer = pdk.Layer(
            'GreatCircleLayer',
            data=df,
            get_source_position=['source_lon', 'source_lat'],
            get_target_position=['target_lon', 'target_lat'],
            get_source_color=[255, 100, 0, 200],  # Orange for source
            get_target_color=[0, 128, 255, 200],  # Blue for target
            get_width=arc_width,
            pickable=True,
            auto_highlight=True,
        )
        
        view_state = pdk.ViewState(
            latitude=40,
            longitude=-30,
            zoom=2.0,
            pitch=0,
            bearing=0,
        )
        
        tooltip = {
            "html": "<b>{spotter}</b> → <b>{dx_station}</b><br/>"
                    "Frequency: {frequency} kHz<br/>"
                    "Mode: {mode}<br/>"
                    "Time: {timestamp}<br/>"
                    "Comment: {comment}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white",
                "fontSize": "12px",
                "padding": "10px"
            }
        }
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style='light' if map_style_option == "Light" else 'dark',
        )
        
        st.pydeck_chart(deck)
        
        st.caption("💡 Hover over arcs to see contact details. Orange markers = spotters, Blue markers = DX stations")
        
        st.divider()
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top 5 Most Spotted Stations**")
            top_dx = df['dx_station'].value_counts().head()
            for call, count in top_dx.items():
                st.text(f"{call}: {count} spots")
        
        with col2:
            st.markdown("**Top 5 Most Active Spotters**")
            top_spotters = df['spotter'].value_counts().head()
            for call, count in top_spotters.items():
                st.text(f"{call}: {count} spots")
        
        # Mode breakdown
        if df['mode'].notna().any():
            st.divider()
            st.markdown("**Mode Breakdown**")
            mode_counts = df['mode'].value_counts()
            st.bar_chart(mode_counts)
        
    except Exception as e:
        st.error(f"Error loading visualization: {str(e)}")
        st.exception(e)
