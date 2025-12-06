import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

from api_client import get_api_client
from db_client import get_db_client
from auth import get_auth_cookie

st.set_page_config(page_title="DX Analysis Dashboard", layout="wide")

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

st.title("📡 Current Conditions")

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
Real-time propagation metrics and band condition analysis.
""")

# Fetch data for metrics
with st.spinner("Loading current conditions..."):
    try:
        # Get spots from last 30 minutes for MOF calculation
        thirty_min_ago = datetime.now() - timedelta(minutes=30)
        recent_spots = api.get_spots(since=thirty_min_ago.isoformat(), limit=1000)
        
        # Get today's 10m FM spots for band status
        today = datetime.now().date()
        today_start = f"{today}T00:00:00"
        fm_spots = api.get_spots(since=today_start, limit=1000)
        
        # Calculate Maximum Observed Frequency (MOF)
        if recent_spots:
            frequencies = [float(spot['frequency']) for spot in recent_spots if spot.get('frequency')]
            # Filter to HF range (7-29.7 MHz = 7000-29700 kHz)
            hf_frequencies = [f for f in frequencies if 7000 <= f <= 29700]
            if hf_frequencies:
                max_freq = max(hf_frequencies)
                mof_mhz = max_freq / 1000  # Convert kHz to MHz
            else:
                mof_mhz = None
        else:
            mof_mhz = None
        
        # Calculate 10m FM Band Status
        if fm_spots:
            # Check if any spots are in FM range (29.6-29.7 MHz = 29600-29700 kHz)
            fm_band_spots = [s for s in fm_spots if 29600 <= float(s.get('frequency', 0)) <= 29700]
            band_status = "OPEN" if fm_band_spots else "CLOSED"
            band_status_delta = f"{len(fm_band_spots)} spots today" if fm_band_spots else "No activity"
        else:
            band_status = "CLOSED"
            band_status_delta = "No data"
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        mof_mhz = None
        band_status = "ERROR"
        band_status_delta = None

st.divider()

# Key Propagation Metrics Section
st.subheader("🔑 Key Propagation Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Create gauge chart for MOF
    if mof_mhz:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=mof_mhz,
            title={'text': "Max Observed Freq (MHz)", 'font': {'size': 14}},
            number={'suffix': " MHz", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [7, 29.7], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [7, 14], 'color': '#ffcccc'},  # Light red
                    {'range': [14, 21], 'color': '#ffffcc'},  # Light yellow
                    {'range': [21, 29.7], 'color': '#ccffcc'}  # Light green
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': mof_mhz
                }
            }
        ))
        fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=40, b=10),
            font={'size': 12}
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Last 30 minutes")
    else:
        st.metric(
            "Maximum Observed Frequency", 
            "No Data", 
            help="Highest frequency with active propagation in the last 30 minutes"
        )

with col2:
    st.metric(
        "10m FM Band Status", 
        band_status,
        delta=band_status_delta,
        delta_color="normal" if band_status == "OPEN" else "off",
        help="Is the 10m FM band (29.6-29.7 MHz) currently open today?"
    )

with col3:
    st.metric("Current Solar Flux", "TBD SFU", help="Solar flux units - indicator of ionospheric conditions")

with col4:
    st.metric("K-Index", "TBD", help="Geomagnetic activity level (0=quiet, 9=severe storm)")

st.markdown("""
**Metric Descriptions:**
- **Maximum Observed Frequency (MOF)**: The highest frequency band showing active propagation, indicates ionospheric conditions
- **10m FM Band Open**: Real-time indicator of whether the 10m FM calling frequency (29.600-29.700 MHz) is experiencing propagation
- **Solar Flux**: Measurement of radio emissions from the sun at 2800 MHz, correlates with HF propagation conditions
- **K-Index**: 3-hour geomagnetic activity index (lower is better for HF propagation)
""")

st.divider()

# Band Conditions Section
st.subheader("📊 Band-by-Band Conditions")

st.markdown("""
**Planned Features:**
- Real-time band status indicators (Open/Marginal/Closed)
- Historical comparison charts
- Band opening/closing predictions
- Regional propagation differences
""")

# Placeholder metrics grid
bands = ["160m", "80m", "40m", "20m", "15m", "10m", "6m"]
col_count = 4
cols = st.columns(col_count)

for idx, band in enumerate(bands):
    with cols[idx % col_count]:
        st.metric(
            f"{band} Status",
            "TBD",
            help=f"Current propagation conditions on {band}"
        )

st.divider()

# 10m Detailed Analysis
st.subheader("📻 10m Band Detailed Analysis")

st.markdown("""
**10m Band Segments:**
- **FM (29.6-29.7 MHz)**: Primary FM simplex calling frequency
- **SSB (28.3-28.6 MHz)**: Single sideband DX and domestic
- **CW (28.0-28.3 MHz)**: Morse code operations
- **Digital (28.0-28.3 MHz)**: FT8, FT4, and other digital modes

**Coming Soon:**
- Real-time segment activity levels
- Distance records by segment
- Band opening duration tracking
- Correlation with solar activity
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("FM Segment (29.6-29.7)", "TBD spots", "TBD% change")

with col2:
    st.metric("SSB Segment (28.3-28.6)", "TBD spots", "TBD% change")

with col3:
    st.metric("CW/Digital (28.0-28.3)", "TBD spots", "TBD% change")

st.divider()

# Propagation Quality Metrics
st.subheader("📈 Propagation Quality Metrics")

st.markdown("""
**Planned Metrics:**
- **MUF (Maximum Usable Frequency)**: Highest frequency usable for a given path
- **LUF (Lowest Usable Frequency)**: Lowest frequency usable without excessive absorption
- **Critical Frequency (foF2)**: Maximum frequency reflected by ionosphere at vertical incidence
- **Signal-to-Noise Ratio Trends**: Quality indicators from spotted signals
- **Path Reliability**: Percentage of successful propagation over time
""")

col1, col2 = st.columns(2)

with col1:
    st.metric("Estimated MUF", "TBD MHz")
    st.metric("Critical Frequency", "TBD MHz")

with col2:
    st.metric("Average SNR", "TBD dB")
    st.metric("Path Reliability", "TBD%")

st.divider()

# Integration Notes
with st.expander("🔧 Grafana Metrics Integration Plan"):
    st.markdown("""
    ### Metrics to Migrate from Grafana
    
    1. **Maximum Observed Frequency (MOF)**
       - Calculate from highest frequency with active spots
       - Update interval: Real-time
       - Source: DX spot frequency data
    
    2. **10m FM Band Open Indicator**
       - Boolean status based on 29.6-29.7 MHz activity
       - Threshold: Configurable spot count in time window
       - Visual: Green (Open) / Red (Closed) indicator
    
    3. **Band Opening Durations**
       - Track continuous periods of activity per band
       - Historical tracking and statistics
    
    4. **Solar Activity Integration**
       - Import SFI, K-index, A-index data
       - Correlate with observed propagation
       - Trend analysis and forecasting
    
    5. **Signal Quality Metrics**
       - Parse signal reports from spot comments
       - Aggregate SNR statistics by band/mode
       - Quality trending over time
    
    ### Data Pipeline
    ```
    API/Database → Metrics Calculator → Cache → Dashboard Display
                                      ↓
                                 Time Series DB (Historical)
    ```
    
    ### Update Strategy
    - Real-time: Every 30-60 seconds
    - Historical: Hourly aggregations
    - Trend data: Daily summaries
    """)

st.divider()

st.info("💡 **Note**: These metrics are currently being monitored in Grafana and will be progressively integrated into this dashboard.")
