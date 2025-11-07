import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Load login state
try:
    with open('login_state.json') as f:
        state = json.load(f)
        st.session_state.logged_in = state.get('logged_in', False)
        st.session_state.user = state.get('user', {})
except FileNotFoundError:
    pass

# Check login
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first. Use the Login page in the sidebar.")
    st.stop()

st.title("DX Propagation Analysis")

# Sidebar welcome and logout
with st.sidebar:
    st.header("User Info")
    st.write(f"Welcome, {st.session_state.user.get('name', 'User')}\n({st.session_state.user.get('callsign', 'N/A')})\nGrid: {st.session_state.user.get('grid', 'N/A')}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = {}
        with open('login_state.json', 'w') as f:
            json.dump({'logged_in': False, 'user': {}}, f)
        st.rerun()

# Select hours
hours = st.selectbox("Select hours for metrics", options=[1, 2, 4, 8, 12, 24, 48], index=2)  # default 4

# API URL - from environment variable with fallback
API_URL = os.getenv("API_URL", "http://dx.jxqz.org:8080/api/spots?band=10m")

# Function to fetch spots
def fetch_spots():
    try:
        response = requests.get(API_URL, verify=False)
        response.raise_for_status()
        data = response.json()
        return data.get('spots', [])  # Extract the spots list
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

spots = fetch_spots()

df = pd.DataFrame()

if spots:
    # Convert to DataFrame
    df = pd.DataFrame(spots)
    # Assuming the API returns a list of dicts with keys like 'call', 'freq', 'time', etc.
    # Adjust column names based on actual API response
    
    # Filter for 10m FM spots in last selected hours
    if 'frequency' in df.columns and 'mode' in df.columns and 'timestamp' in df.columns:
        now = pd.Timestamp.now()
        last_hours = now - pd.Timedelta(hours=hours)
        filtered_df_fm = df[
            (df['frequency'].astype(float).between(29600, 29700)) &
            (pd.to_datetime(df['timestamp'], errors='coerce') > last_hours)
        ]
        count_10m_fm = len(filtered_df_fm)
        st.metric(f"10m FM Spots (Last {hours}h)", count_10m_fm)
        
        # Filter for 10m SSB spots in last selected hours
        filtered_df_ssb = df[
            (df['frequency'].astype(float).between(28300, 28600)) &
            (pd.to_datetime(df['timestamp'], errors='coerce') > last_hours)
        ]
        count_10m_ssb = len(filtered_df_ssb)
        st.metric(f"10m SSB Spots (Last {hours}h)", count_10m_ssb)
    
else:
    st.write("No spots available.")

# Display last updated time
st.caption(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Display max age of spots
if not df.empty:
    oldest = pd.to_datetime(df['timestamp'], errors='coerce').min()
    if pd.notna(oldest):
        age = pd.Timestamp.now() - oldest
        age_hours = abs(age.total_seconds() / 3600)
        st.metric("Max Age of Spots", f"{age_hours:.1f} hours")

# Auto-refresh every 5 minutes
import time
time.sleep(300)
st.rerun()