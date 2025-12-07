import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import plotly.graph_objects as go
import pytz

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
        
        # Get latest solar data
        solar_data = db.get_latest_solar_data()
        
        # Calculate band-by-band conditions (last 30 minutes)
        band_conditions = {}
        band_ranges = {
            "40m": {"full": (7000, 7300), "voice": (7125, 7300)},      # CW: 7000-7125, Voice: 7125-7300
            "20m": {"full": (14000, 14350), "voice": (14150, 14350)},  # CW: 14000-14150, Voice: 14150-14350
            "17m": {"full": (18068, 18168), "voice": (18110, 18168)},  # CW: 18068-18110, Voice: 18110-18168
            "15m": {"full": (21000, 21450), "voice": (21200, 21450)},  # CW: 21000-21200, Voice: 21200-21450
            "12m": {"full": (24890, 24990), "voice": (24930, 24990)},  # CW: 24890-24930, Voice: 24930-24990
            "10m": {"full": (28000, 29700), "voice": (28300, 29700)}   # CW: 28000-28300, Voice: 28300-29700
        }
        
        for band, ranges in band_ranges.items():
            # Get spots in the full band range
            band_spots = [s for s in recent_spots if ranges["full"][0] <= float(s.get('frequency', 0)) <= ranges["full"][1]]
            # Get spots in voice portion
            voice_spots = [s for s in recent_spots if ranges["voice"][0] <= float(s.get('frequency', 0)) <= ranges["voice"][1]]
            
            spot_count = len(band_spots)
            voice_count = len(voice_spots)
            
            if spot_count == 0:
                status = "CLOSED"
                color = "off"
            elif voice_count >= 2:
                status = "OPEN"
                color = "normal"
            else:
                status = "MARGINAL"
                color = "inverse"
            
            band_conditions[band] = {
                "status": status,
                "count": spot_count,
                "color": color
            }
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        mof_mhz = None
        band_status = "ERROR"
        band_status_delta = None
        solar_data = None
        band_conditions = {}

st.divider()

# Solar Indicators Section
st.subheader("☀️ Solar Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    ssn_value = int(solar_data['sunspot_number']) if solar_data and solar_data.get('sunspot_number') is not None else "No Data"
    if solar_data and solar_data.get('timestamp'):
        # Convert UTC to local timezone
        local_tz = datetime.now().astimezone().tzinfo
        local_time = solar_data['timestamp'].replace(tzinfo=pytz.UTC).astimezone(local_tz)
        ssn_timestamp = local_time.strftime("%H:%M %Z")
    else:
        ssn_timestamp = ""
    st.metric(
        "Sunspot Number", 
        ssn_value,
        help="Daily Sunspot Number (SSN) - Higher numbers indicate better HF propagation conditions"
    )
    if ssn_timestamp:
        st.caption(f"Updated: {ssn_timestamp}")

with col2:
    sfi_value = int(solar_data['solar_flux']) if solar_data and solar_data.get('solar_flux') is not None else "No Data"
    if solar_data and solar_data.get('timestamp'):
        # Convert UTC to local timezone
        local_tz = datetime.now().astimezone().tzinfo
        local_time = solar_data['timestamp'].replace(tzinfo=pytz.UTC).astimezone(local_tz)
        sfi_timestamp = local_time.strftime("%H:%M %Z")
    else:
        sfi_timestamp = ""
    sfi_display = f"{sfi_value} SFU" if isinstance(sfi_value, int) else sfi_value
    st.metric(
        "Solar Flux Index", 
        sfi_display,
        help="Solar flux at 2800 MHz (SFI) - indicator of ionospheric conditions (70-300+ SFU typical range)"
    )
    if sfi_timestamp:
        st.caption(f"Updated: {sfi_timestamp}")

with col3:
    k_value = int(solar_data['k_index']) if solar_data and solar_data.get('k_index') is not None else "No Data"
    if solar_data and solar_data.get('timestamp'):
        # Convert UTC to local timezone
        local_tz = datetime.now().astimezone().tzinfo
        local_time = solar_data['timestamp'].replace(tzinfo=pytz.UTC).astimezone(local_tz)
        k_timestamp = local_time.strftime("%H:%M %Z")
    else:
        k_timestamp = ""
    st.metric(
        "K-Index", 
        k_value,
        help="Geomagnetic activity index (0-9 scale) - Lower is better for HF propagation"
    )
    if k_timestamp:
        st.caption(f"Updated: {k_timestamp}")

st.divider()

# Real-Time Spot-Based Metrics Section
st.subheader("📊 Real-Time Spot Analysis")

col1, col2 = st.columns(2)

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

st.markdown("""
**Metric Descriptions:**
- **Maximum Observed Frequency (MOF)**: The highest frequency band showing active propagation, indicates ionospheric conditions
- **10m FM Band Open**: Real-time indicator of whether the 10m FM calling frequency (29.600-29.700 MHz) is experiencing propagation
- **Sunspot Number (SSN)**: Daily count of sunspots on the solar disk. Higher numbers (100+) indicate better HF propagation, especially on higher bands
- **Solar Flux Index (SFI)**: Measurement of radio emissions from the sun at 2800 MHz (2.8 GHz). Values: 70-100=poor, 100-150=fair, 150+=good HF conditions
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

# Band conditions grid (last 30 minutes)
bands = ["40m", "20m", "17m", "15m", "12m", "10m"]
cols = st.columns(len(bands))

status_colors = {
    "OPEN": "#28a745",    # Green
    "MARGINAL": "#ffc107", # Yellow
    "CLOSED": "#dc3545"    # Red
}

for idx, band in enumerate(bands):
    with cols[idx]:
        if band in band_conditions:
            cond = band_conditions[band]
            color = status_colors.get(cond["status"], "#666666")
            st.markdown(f"**{band} Status**")
            st.markdown(f"<div style='font-size: 24px; font-weight: bold; color: {color};'>{cond['status']}</div>", unsafe_allow_html=True)
            st.caption(f"{cond['count']} spots")
        else:
            st.markdown(f"**{band} Status**")
            st.markdown(f"<div style='font-size: 24px; font-weight: bold; color: #dc3545;'>ERROR</div>", unsafe_allow_html=True)

st.caption("Last 30 minutes • CLOSED: 0 spots • MARGINAL: 1+ spots (includes CW/Digital) • OPEN: 2+ voice spots")

st.divider()

# DX Band Detailed Analysis
st.subheader("📻 Mobile DX Band Analysis")

st.markdown("""
**Prime DX Bands for 100W Mobile Operations:**

Detailed segment activity analysis for 15m, 12m, and 10m bands - optimized for mobile HF DX with modest power.
""")

# Time frame selector for band analysis
analysis_hours = st.selectbox(
    "Time Window for Analysis",
    options=[1, 2, 4, 6, 12],
    index=1,  # Default to 2 hours
    format_func=lambda x: f"Last {x} hour{'s' if x > 1 else ''}",
    key="band_analysis_timeframe"
)

# Prepare data for visualizations
with st.spinner(f"Loading {analysis_hours} hour(s) of data..."):
    # Fetch spots for selected time window - use UTC time
    from datetime import timezone
    analysis_time_ago = datetime.now(timezone.utc) - timedelta(hours=analysis_hours)
    # Format as ISO string and replace +00:00 with Z for compatibility
    analysis_since_param = analysis_time_ago.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    
    # Fetch spots using frequency range (21 MHz to 29.7 MHz covers 15m, 12m, and 10m)
    import importlib
    import api_client as api_module
    importlib.reload(api_module)
    fresh_api = api_module.DXApiClient()
    
    base_url = os.getenv('API_BASE_URL', 'http://localhost:8080')
    frequency_min = 21000  # 21 MHz (15m band start)
    frequency_max = 29700  # 29.7 MHz (10m FM end)
    
    # Make single API call with frequency range
    # Debug: Show actual query URL (uncomment to debug API calls)
    # query_url = f"{base_url}/api/spots?since={analysis_since_param}&limit=1000&frequency_min={frequency_min}&frequency_max={frequency_max}"
    # st.code(query_url, language=None)
    
    analysis_spots = fresh_api._make_request('/api/spots', {
        'since': analysis_since_param,
        'limit': 1000,
        'frequency_min': frequency_min,
        'frequency_max': frequency_max
    }).get('spots', [])
    
    # Debug: Check if API is actually filtering by time
    if analysis_spots:
        spot_times = [datetime.fromisoformat(s['time'].replace('Z', '+00:00')) for s in analysis_spots if s.get('time')]
        if spot_times:
            oldest_spot = min(spot_times)
            newest_spot = max(spot_times)
            time_range_hours = (newest_spot - oldest_spot).total_seconds() / 3600
            
            # Show how long ago the oldest spot is
            hours_ago = (datetime.now(oldest_spot.tzinfo) - oldest_spot).total_seconds() / 3600
            
            # Count spots by band for debugging
            band_counts = {"15m": 0, "12m": 0, "10m": 0, "other": 0}
            for spot in analysis_spots:
                freq = float(spot.get('frequency', 0))
                if 21000 <= freq <= 21450:
                    band_counts["15m"] += 1
                elif 24890 <= freq <= 24990:
                    band_counts["12m"] += 1
                elif 28000 <= freq <= 29700:
                    band_counts["10m"] += 1
                else:
                    band_counts["other"] += 1
            
            st.success(f"📊 **{len(analysis_spots)} total spots** | Time range: {time_range_hours:.1f}h | Oldest: {hours_ago:.1f}h ago | 15m: {band_counts['15m']} | 12m: {band_counts['12m']} | 10m: {band_counts['10m']} | Other: {band_counts['other']}")
        else:
            st.caption(f"📊 Loaded {len(analysis_spots)} spots")
    else:
        st.warning(f"No spots found in the last {analysis_hours} hour(s)")
        analysis_spots = []

try:
    # Define segments for the three prime DX bands
    dx_band_segments = {
        "15m": {
            "CW/Digital": (21000, 21200),
            "SSB": (21200, 21450)
        },
        "12m": {
            "CW/Digital": (24890, 24930),
            "SSB": (24930, 24990)
        },
        "10m": {
            "CW/Digital": (28000, 28300),
            "SSB": (28300, 28600),
            "FM": (29600, 29700)
        }
    }
    
    # Calculate activity counts and collect frequencies for scatter plot
    segment_counts = []
    frequency_data = []
    
    for band, segments in dx_band_segments.items():
        for segment, (low, high) in segments.items():
            spots_in_segment = [s for s in analysis_spots if low <= float(s.get('frequency', 0)) <= high]
            count = len(spots_in_segment)
            segment_counts.append({
                "Band": band,
                "Segment": segment,
                "Count": count
            })
            
            # Collect frequencies for scatter plot
            for spot in spots_in_segment:
                frequency_data.append({
                    "Band": band,
                    "Frequency": float(spot['frequency']) / 1000  # Convert to MHz
                })
    
    # Create visualizations side by side
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Bar chart: Activity by band and segment
        if segment_counts:
            df_counts = pd.DataFrame(segment_counts)
            fig_bar = go.Figure()
            
            # Get unique segments (modes)
            segments = df_counts["Segment"].unique()
            segment_colors = {
                "CW/Digital": "#9B59B6",
                "SSB": "#3498DB",
                "FM": "#E74C3C"
            }
            
            # Group by segment (mode)
            for segment in segments:
                segment_data = df_counts[df_counts["Segment"] == segment]
                fig_bar.add_trace(go.Bar(
                    name=segment,
                    x=segment_data["Band"],
                    y=segment_data["Count"],
                    text=segment_data["Count"],
                    textposition='auto',
                    marker_color=segment_colors.get(segment, "#95A5A6")
                ))
            
            fig_bar.update_layout(
                title="Activity by Band & Segment",
                xaxis_title="Band",
                yaxis_title="Number of Spots",
                barmode='group',
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=["15m", "12m", "10m"]
                )
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No activity in the last 30 minutes")
    
    with viz_col2:
        # Scatter plot: Frequency distribution within bands (normalized)
        if frequency_data:
            df_freq = pd.DataFrame(frequency_data)
            fig_scatter = go.Figure()
            
            colors = {"15m": "#FF6B6B", "12m": "#4ECDC4", "10m": "#45B7D1"}
            
            # Band ranges for normalization
            band_ranges = {
                "15m": (21.0, 21.45),
                "12m": (24.89, 24.99),
                "10m": (28.0, 29.7)
            }
            
            for band in ["15m", "12m", "10m"]:
                band_data = df_freq[df_freq["Band"] == band]
                if len(band_data) > 0:
                    band_min, band_max = band_ranges[band]
                    
                    # Normalize frequencies to 0-100 scale within each band
                    normalized_freqs = []
                    hover_texts = []
                    for freq in band_data["Frequency"]:
                        normalized = ((freq - band_min) / (band_max - band_min)) * 100
                        normalized_freqs.append(normalized)
                        hover_texts.append(f"{freq:.3f} MHz")
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=[band] * len(band_data),
                        y=normalized_freqs,
                        mode='markers',
                        name=band,
                        marker=dict(
                            size=8,
                            color=colors[band],
                            opacity=0.6,
                            line=dict(width=1, color='white')
                        ),
                        text=hover_texts,
                        hovertemplate='%{text}<extra></extra>'
                    ))
            
            fig_scatter.update_layout(
                title="Frequency Distribution Within Bands (Normalized)",
                xaxis_title="Band",
                yaxis_title="Position in Band (%)",
                height=400,
                showlegend=False,
                yaxis=dict(
                    range=[0, 100],
                    gridcolor='lightgray',
                    ticksuffix='%'
                ),
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=["15m", "12m", "10m"]
                )
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No frequency data to display")
    
except Exception as e:
    st.error(f"Error generating visualizations: {e}")

st.divider()

# Segment details
st.markdown("### Band Segment Details")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**15m Band (21 MHz)**")
    st.caption("CW/Digital: 21.0-21.2 MHz")
    st.caption("SSB: 21.2-21.45 MHz")

with col2:
    st.markdown("**12m Band (24 MHz)**")
    st.caption("CW/Digital: 24.89-24.93 MHz")
    st.caption("SSB: 24.93-24.99 MHz")

with col3:
    st.markdown("**10m Band (28-29.7 MHz)**")
    st.caption("CW/Digital: 28.0-28.3 MHz")
    st.caption("SSB: 28.3-28.6 MHz")
    st.caption("FM: 29.6-29.7 MHz")


