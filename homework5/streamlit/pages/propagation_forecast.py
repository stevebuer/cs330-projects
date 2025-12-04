import streamlit as st
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

st.set_page_config(page_title="Propagation Forecast", layout="wide")

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

st.title("🔮 Propagation Forecast")

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
ML-powered predictions for future propagation conditions based on historical patterns and current trends.
""")

st.info("🚧 **Coming Soon**: This page will feature machine learning models for propagation forecasting.")

st.divider()

# Placeholder sections for future ML implementation

st.subheader("📈 24-Hour Forecast")
st.markdown("""
**Upcoming features:**
- Band-by-band propagation predictions
- Confidence intervals for forecasts
- Best operating times by band
- Expected signal strength patterns
""")

st.divider()

st.subheader("🎯 Best Operating Times")
st.markdown("""
**Upcoming features:**
- Optimal times for each band
- Geographic region predictions
- Mode-specific recommendations
- Solar conditions impact
""")

st.divider()

st.subheader("🌐 Geographic Predictions")
st.markdown("""
**Upcoming features:**
- Predicted propagation paths
- Regional activity forecasts
- DX opportunity alerts
- Long-path vs short-path predictions
""")

st.divider()

st.subheader("🤖 Model Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Planned ML Models:**
    - LSTM neural networks for time-series forecasting
    - Random Forest for band condition classification
    - Transformer models for sequence prediction
    - Ensemble methods for improved accuracy
    """)

with col2:
    st.markdown("""
    **Training Data Sources:**
    - Historical DX spot patterns
    - Solar flux indices (SFI)
    - Geomagnetic activity (K-index, A-index)
    - Seasonal and diurnal patterns
    """)

st.divider()

# Development preview section
with st.expander("🔧 Development Preview"):
    st.markdown("""
    ### Integration Plan
    
    1. **Data Collection Phase**
       - Accumulate historical spot data
       - Integrate solar activity data
       - Build feature engineering pipeline
    
    2. **Model Development Phase**
       - Train LSTM models on time-series data
       - Validate against holdout test sets
       - Tune hyperparameters for accuracy
    
    3. **Deployment Phase**
       - Real-time inference pipeline
       - Model versioning and updates
       - Performance monitoring
       
    4. **User Features Phase**
       - Interactive forecast charts
       - Customizable prediction windows
       - Alert system for favorable conditions
       - Export forecast data
    """)
    
    st.info("Check back soon for updates as ML models are integrated into the dashboard!")
