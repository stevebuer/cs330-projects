import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from api_client import get_api_client
from db_client import get_db_client
from auth import get_auth_cookie

st.set_page_config(page_title="Latest Spots", layout="wide")

# Get clients
api = get_api_client()
db = get_db_client()

# Initialize session state for user (to access timezone)
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

st.title("📡 Latest DX Spots")

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

col1, col2 = st.columns(2)

with col1:
    band = st.selectbox("Band", options=["All Bands", "40m", "30m", "20m", "17m", "15m", "12m", "10m"], index=0)

with col2:
    limit = st.selectbox("Number of spots", options=[10, 25, 50, 100], index=0)

# Fetch data from API
with st.spinner("Fetching latest spots..."):
    import requests
    import socket
    try:
        # Force IPv4 connection
        old_getaddrinfo = socket.getaddrinfo
        
        def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return old_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        
        socket.getaddrinfo = getaddrinfo_ipv4_only
        
        try:
            # Build URL with optional band filter
            url = f"http://api.jxqz.org:8080/api/spots/recent?limit={limit}"
            if band != "All Bands":
                url += f"&band={band}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            spots = data.get('spots', data) if isinstance(data, dict) else data
        finally:
            socket.getaddrinfo = old_getaddrinfo
            
    except Exception as e:
        st.error(f"API request failed: {e}")
        st.info("Tip: Check that API is accessible and not blocking IPv6")
        spots = []

if spots:
    df = pd.DataFrame(spots)
    
    # Convert timestamp to user's timezone
    if 'timestamp' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Apply user's timezone if logged in
        if st.session_state.get('logged_in') and st.session_state.get('user', {}).get('timezone'):
            import pytz
            user_tz = st.session_state.user.get('timezone', 'UTC')
            try:
                tz = pytz.timezone(user_tz)
                df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(tz)
                st.caption(f"Times displayed in: {user_tz}")
            except:
                st.caption("Times displayed in: UTC")
        else:
            st.caption("Times displayed in: UTC (login to use your timezone)")
    
    st.dataframe(df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="dx_spots.csv",
        mime="text/csv"
    )
else:
    st.warning("No data available. Check that the API is running and accessible.")
    st.info(f"API URL: {api.base_url}")
