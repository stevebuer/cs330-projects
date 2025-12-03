import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="DX Propagation Dashboard", layout="wide")

# Initialize session state for user
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

# Database connection parameters from environment
DB_HOST = os.getenv('PGHOST', 'localhost')
DB_PORT = os.getenv('PGPORT', '5432')
DB_NAME = os.getenv('PGDATABASE', 'dx_analysis')
DB_USER = os.getenv('PGUSER', 'dx_web_user')
DB_PASSWORD = os.getenv('PGPASSWORD', '')

@st.cache_resource
def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_recent_spots(hours=24):
    """Fetch recent DX spots from database"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    query = """
    SELECT 
        timestamp,
        dx_call,
        frequency,
        spotter_call,
        comment,
        mode,
        signal_report,
        grid_square,
        band
    FROM dx_spots
    WHERE timestamp > NOW() - INTERVAL '%s hours'
    ORDER BY timestamp DESC
    LIMIT 1000
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(hours,))
        return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

st.title("🌍 DX Propagation Dashboard")

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
    auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
    
    if st.button("🔄 Refresh Now"):
        st.cache_resource.clear()
        st.rerun()

# Fetch data
df = fetch_recent_spots(hours)

if df.empty:
    st.warning("No data available")
    st.stop()

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_spots = len(df)
    st.metric("Total Spots", f"{total_spots:,}")

with col2:
    unique_dx = df['dx_call'].nunique()
    st.metric("Unique DX Stations", unique_dx)

with col3:
    unique_spotters = df['spotter_call'].nunique()
    st.metric("Active Spotters", unique_spotters)

with col4:
    if 'timestamp' in df.columns:
        latest = pd.to_datetime(df['timestamp']).max()
        age_minutes = (datetime.now() - latest.to_pydatetime()).total_seconds() / 60
        st.metric("Latest Spot", f"{age_minutes:.0f}m ago")

# Band analysis
st.subheader("📊 Band Activity")

# 10m breakdown
df_10m = df[df['frequency'].between(28000, 29700)]
col1, col2, col3 = st.columns(3)

with col1:
    fm_spots = df[df['frequency'].between(29600, 29700)]
    st.metric("10m FM (29.6-29.7)", len(fm_spots))

with col2:
    ssb_spots = df[df['frequency'].between(28300, 28600)]
    st.metric("10m SSB (28.3-28.6)", len(ssb_spots))

with col3:
    cw_spots = df[df['frequency'].between(28000, 28300)]
    st.metric("10m CW (28.0-28.3)", len(cw_spots))

# Recent spots table
st.subheader("📡 Recent Spots")
display_df = df[['timestamp', 'frequency', 'dx_call', 'spotter_call', 'band', 'comment']].head(50)
st.dataframe(display_df, use_container_width=True)

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(60)
    st.rerun()
