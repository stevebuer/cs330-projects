import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom clients
from api_client import get_api_client
from db_client import get_db_client

st.set_page_config(page_title="World Map", layout="wide")

# Initialize session state for user
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

# Get clients
api = get_api_client()
db = get_db_client()

def fetch_recent_spots(hours=24):
    """Fetch recent DX spots from API"""
    spots = api.get_spots(hours=hours, limit=1000)
    
    if not spots:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(spots)
    
    # Convert timestamp strings to datetime if needed
    if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

st.title("🌍 World Map")

st.markdown("""
Interactive 3D visualization of DX spots and propagation paths using PyDeck.
""")

st.info("🚧 **Coming Soon**: Interactive globe showing real-time DX spots, propagation paths, and geographic patterns.")

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
    hours = st.selectbox("Time Window", options=[1, 2, 4, 8, 12, 24, 48], index=5)
    
    st.divider()
    
    st.subheader("Map Controls (Coming Soon)")
    map_style = st.selectbox("Map Style", ["Dark", "Light", "Satellite"], disabled=True)
    show_paths = st.checkbox("Show Propagation Paths", value=True, disabled=True)
    show_spotters = st.checkbox("Show Spotter Locations", value=True, disabled=True)
    show_dx = st.checkbox("Show DX Locations", value=True, disabled=True)

st.divider()

# Placeholder visualization
st.subheader("🗺️ PyDeck Globe Visualization")

st.markdown("""
**Planned Features:**

- **3D Globe View**: Interactive rotating globe with DX spot locations
- **Propagation Paths**: Arc layers showing spotter-to-DX connections
- **Heat Maps**: Geographic density of activity
- **Time Animation**: Watch propagation patterns evolve over time
- **Band Filtering**: Toggle visibility by band
- **Grid Square Overlay**: Maidenhead locator grid display
- **Zoom Controls**: Focus on specific regions or view global patterns
- **Elevation Profiles**: Great circle paths with terrain elevation

**Visualization Layers:**
- Spotter locations (marker layer)
- DX station locations (marker layer)
- Propagation paths (arc layer)
- Activity heat map (hexagon layer)
- Grid square boundaries (path layer)
""")

# Mock data preview
with st.expander("🔧 Technical Implementation Preview"):
    st.markdown("""
    ### PyDeck Integration
    
    ```python
    import pydeck as pdk
    
    # Example layer configuration:
    arc_layer = pdk.Layer(
        'ArcLayer',
        data=spots_df,
        get_source_position=['spotter_lon', 'spotter_lat'],
        get_target_position=['dx_lon', 'dx_lat'],
        get_source_color=[255, 0, 0, 160],
        get_target_color=[0, 255, 0, 160],
        get_width=2,
        pickable=True
    )
    
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        data=spots_df,
        get_position=['dx_lon', 'dx_lat'],
        get_radius=50000,
        get_fill_color=[0, 255, 0, 200],
        pickable=True
    )
    
    view_state = pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1.5,
        pitch=45
    )
    
    deck = pdk.Deck(
        layers=[arc_layer, scatter_layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/dark-v10'
    )
    
    st.pydeck_chart(deck)
    ```
    
    ### Data Requirements
    - Geocoding of callsigns to lat/lon coordinates
    - Grid square to coordinate conversion
    - Great circle path calculations
    - Real-time data streaming for live updates
    """)

st.divider()

st.info("💡 **Tip**: Visit 'Latest Spots' and 'Current Conditions' pages for current data while the map is under development.")
