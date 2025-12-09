import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
import json
from openai import OpenAI

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file if running locally (not in Docker container)
# In Docker, environment variables are passed via docker-compose
if os.path.exists('/app/streamlit'):
    # Running in Docker - env vars already loaded from docker-compose
    pass
else:
    # Running locally - load from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    load_dotenv(env_path)

from api_client import get_api_client
from db_client import get_db_client
from auth import get_auth_cookie

st.set_page_config(page_title="Propagation Forecast", layout="wide", page_icon="🔮")

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

# Initialize forecast cache in session state
if 'forecast_cache' not in st.session_state:
    st.session_state.forecast_cache = {}
if 'forecast_timestamp' not in st.session_state:
    st.session_state.forecast_timestamp = None

st.title("🔮 HF Propagation Forecast")

st.markdown("""
AI-powered propagation forecast based on recent DX cluster activity patterns.
This forecast analyzes recent spot data to predict propagation conditions for the next 1-3 days.
""")

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
    
    st.header("⚙️ Forecast Settings")
    forecast_days = st.selectbox("Forecast Period", [1, 2, 3], index=1, help="Number of days to forecast")
    
    st.divider()
    
    if st.button("🔄 Generate New Forecast", use_container_width=True):
        st.session_state.forecast_cache = {}
        st.session_state.forecast_timestamp = None
        st.rerun()
        st.divider()

# Helper Functions

def collect_dx_statistics():
    """
    Collect and analyze DX spot data from multiple time periods.
    Returns statistical summary for LLM analysis.
    """
    stats = {
        'last_24h': {},
        'last_7d': {},
        'last_30d': {}
    }
    
    time_periods = [
        ('last_24h', 24),
        ('last_7d', 24 * 7),
        ('last_30d', 24 * 30)
    ]
    
    for period_name, hours in time_periods:
        try:
            spots = api.get_spots(hours=hours, limit=5000)
            
            if spots:
                df = pd.DataFrame(spots)
                
                # Band distribution analysis
                if 'band' in df.columns:
                    band_counts = df['band'].value_counts().to_dict()
                    stats[period_name]['band_distribution'] = band_counts
                    stats[period_name]['total_spots'] = len(df)
                    stats[period_name]['active_bands'] = len(band_counts)
                
                # Geographic distribution (callsign prefixes)
                if 'dx_call' in df.columns:
                    top_dx = df['dx_call'].value_counts().head(10).to_dict()
                    stats[period_name]['top_dx_stations'] = top_dx
                    
                    # Extract prefix patterns
                    prefixes = df['dx_call'].str[:2].value_counts().head(15).to_dict()
                    stats[period_name]['top_prefixes'] = prefixes
                    stats[period_name]['unique_prefixes'] = df['dx_call'].str[:2].nunique()
        except Exception as e:
            st.warning(f"Error collecting {period_name} data: {e}")
            continue
    
    return stats


def generate_forecast_with_llm(stats, forecast_days=2):
    """
    Generate propagation forecast using OpenAI GPT-4.
    
    Args:
        stats: Statistical summary from collect_dx_statistics()
        forecast_days: Number of days to forecast (1-3)
    
    Returns:
        str: Formatted forecast text
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "⚠️ **Configuration Error**: OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file."
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Construct prompt with statistical context
        prompt = f"""You are an expert amateur radio propagation analyst. Based on the following DX cluster activity data, provide a detailed {forecast_days}-day propagation forecast.

RECENT ACTIVITY DATA:

Last 24 Hours:
- Total spots: {stats['last_24h'].get('total_spots', 0)}
- Active bands: {stats['last_24h'].get('active_bands', 0)}
- Band distribution: {json.dumps(stats['last_24h'].get('band_distribution', {}), indent=2)}
- Top DX prefixes: {json.dumps(stats['last_24h'].get('top_prefixes', {}), indent=2)}
- Unique regions: {stats['last_24h'].get('unique_prefixes', 0)}

Last 7 Days:
- Total spots: {stats['last_7d'].get('total_spots', 0)}
- Active bands: {stats['last_7d'].get('active_bands', 0)}
- Band distribution: {json.dumps(stats['last_7d'].get('band_distribution', {}), indent=2)}

Based on this data, provide a {forecast_days}-day forecast that includes:

1. **Overall Propagation Outlook**: General conditions expected
2. **Band-by-Band Forecast**: Specific predictions for key bands
3. **Best Times**: Recommended operating times
4. **DX Opportunities**: Geographic regions likely to be workable
5. **Confidence Level**: Rate your confidence (Low/Medium/High)

Consider that higher bands (10m, 12m, 15m) active indicates good solar conditions.
Format your response clearly for radio operators."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert amateur radio propagation analyst with deep knowledge of HF propagation, solar cycles, and DX conditions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"⚠️ **Error generating forecast**: {str(e)}"


# Check cache
cache_key = f"forecast_{forecast_days}d"
cache_ttl = timedelta(hours=12)

show_cached = False
if cache_key in st.session_state.forecast_cache and st.session_state.forecast_timestamp:
    age = datetime.now() - st.session_state.forecast_timestamp
    if age < cache_ttl:
        show_cached = True

if show_cached:
    st.success("📋 Showing cached forecast (refreshed every 12 hours)")
    forecast_text = st.session_state.forecast_cache[cache_key]
    cache_age = datetime.now() - st.session_state.forecast_timestamp
    hours_old = cache_age.total_seconds() / 3600
    st.caption(f"Generated {hours_old:.1f} hours ago")
else:
    with st.spinner("🤖 Analyzing DX cluster data and generating AI forecast..."):
        # Collect statistics
        stats = collect_dx_statistics()
        
        if not stats or not stats['last_24h']:
            st.error("Unable to collect DX spot statistics. Please try again later.")
            st.stop()
        
        # Generate forecast
        forecast_text = generate_forecast_with_llm(stats, forecast_days)
        
        # Cache the result
        st.session_state.forecast_cache[cache_key] = forecast_text
        st.session_state.forecast_timestamp = datetime.now()

# Display the forecast
st.markdown("---")
st.markdown(forecast_text)
st.markdown("---")

# Display statistics summary
with st.expander("📊 View Data Summary"):
    stats = collect_dx_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("24h Spots", stats['last_24h'].get('total_spots', 0))
        st.metric("Active Bands", stats['last_24h'].get('active_bands', 0))
    
    with col2:
        st.metric("7d Spots", stats['last_7d'].get('total_spots', 0))
        avg_daily = stats['last_7d'].get('total_spots', 0) / 7
        st.metric("7d Daily Avg", f"{avg_daily:.0f}")
    
    with col3:
        st.metric("Unique Regions", stats['last_24h'].get('unique_prefixes', 0))
        trend = "📈" if stats['last_24h'].get('total_spots', 0) > avg_daily else "📉"
        st.metric("Trend", trend)
    
    st.divider()
    
    st.subheader("Band Activity (Last 24h)")
    if 'band_distribution' in stats['last_24h']:
        band_df = pd.DataFrame([
            {"Band": band, "Spots": count}
            for band, count in sorted(stats['last_24h']['band_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True)
        ])
        st.bar_chart(band_df.set_index('Band'))

st.divider()

# Model information
st.subheader("🤖 About This Forecast")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Forecast Method:**
    - Uses OpenAI GPT-4-mini LLM
    - Analyzes 24h, 7d, 30d spot patterns
    - Considers band activity and geographic diversity
    - Cached for 12 hours to optimize API usage
    """)

with col2:
    st.markdown("""
    **Data Sources:**
    - Real-time DX cluster spots
    - Band activity distribution
    - Geographic region patterns
    - Historical trend analysis
    """)

st.info("💡 **Note**: This is an AI-generated forecast based on recent DX activity patterns. For official propagation data, consult NOAA Space Weather Prediction Center.")
