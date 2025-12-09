import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from db_client import get_db_client
from auth import (
    hash_password, verify_password, generate_session_token,
    set_auth_cookie, get_auth_cookie, clear_auth_cookie
)

st.set_page_config(page_title="User Login", layout="centered")

# Get database client
db = get_db_client()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

# Check for existing session from cookie on page load
if not st.session_state.logged_in:
    auth_data = get_auth_cookie()
    if auth_data:
        # Validate session token
        user_data = db.get_user_by_session(auth_data['session_token'])
        if user_data:
            st.session_state.logged_in = True
            st.session_state.user = user_data
            st.success("✅ Logged in automatically from saved session")
            st.rerun()

st.title("🔐 User Login")

st.markdown("""
Secure password-based authentication with persistent sessions.
""")

if not st.session_state.logged_in:
    # Login / Register Tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            callsign = st.text_input("Callsign", max_chars=20).upper()
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me (30 days)", value=True)
            
            submitted = st.form_submit_button("Login", type="primary", width='stretch')
            
            if submitted:
                if not callsign or not password:
                    st.error("Please enter both callsign and password")
                else:
                    # Authenticate user
                    user_data = db.authenticate_user(callsign)
                    
                    if user_data and user_data.get('password_hash'):
                        if verify_password(password, user_data['password_hash']):
                            # Generate session token
                            session_token = generate_session_token()
                            
                            # Save session to database
                            if db.save_session_token(callsign, session_token, days=30 if remember_me else 1):
                                # Set cookie
                                if remember_me:
                                    set_auth_cookie(callsign, session_token, days=30)
                                
                                # Update session state
                                st.session_state.logged_in = True
                                st.session_state.user = user_data
                                st.success(f"Welcome back, {callsign}!")
                                st.rerun()
                            else:
                                st.error("Failed to create session. Please try again.")
                        else:
                            st.error("Invalid password")
                    else:
                        st.error("User not found. Please register first.")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            new_callsign = st.text_input("Callsign *", max_chars=20, key="reg_callsign").upper()
            new_password = st.text_input("Password *", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password *", type="password", key="reg_confirm")
            
            st.divider()
            
            new_name = st.text_input("Name (optional)", max_chars=100)
            new_grid = st.text_input("Grid Square (optional)", max_chars=6, help="e.g., CN87").upper()
            new_email = st.text_input("Email (optional)", help="For notifications and alerts")
            new_phone = st.text_input("Phone (optional)", help="For SMS alerts (include country code)")
            
            submitted = st.form_submit_button("Register", type="primary", width='stretch')
            
            if submitted:
                if not new_callsign or not new_password:
                    st.error("Callsign and password are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    # Check if user already exists
                    existing = db.authenticate_user(new_callsign)
                    if existing and existing.get('password_hash'):
                        st.error(f"Callsign {new_callsign} is already registered. Please login instead.")
                    else:
                        # Hash password and create user
                        password_hash = hash_password(new_password)
                        user_data = db.create_user_with_password(
                            new_callsign, password_hash, new_name, new_grid,
                            new_email if new_email else None,
                            new_phone if new_phone else None
                        )
                        
                        if user_data:
                            # Generate session token
                            session_token = generate_session_token()
                            db.save_session_token(new_callsign, session_token)
                            set_auth_cookie(new_callsign, session_token)
                            
                            st.session_state.logged_in = True
                            st.session_state.user = user_data
                            st.success(f"Welcome, {new_callsign}! Your account has been created.")
                            st.rerun()
                        else:
                            st.error("Failed to create account. Please try again.")

else:
    # User is logged in - show profile and settings
    st.success(f"✅ Logged in as **{st.session_state.user['callsign']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.user.get('name'):
            st.write(f"**Name:** {st.session_state.user['name']}")
        if st.session_state.user.get('grid_square'):
            st.write(f"**Grid Square:** {st.session_state.user['grid_square']}")
    with col2:
        if st.session_state.user.get('email'):
            st.write(f"**Email:** {st.session_state.user['email']}")
        if st.session_state.user.get('phone'):
            st.write(f"**Phone:** {st.session_state.user['phone']}")
    
    st.divider()
    
    # Profile Settings
    with st.expander("📝 Profile Settings", expanded=False):
        with st.form("update_profile_form"):
            st.subheader("Update Profile Information")
            
            new_name = st.text_input("Name", value=st.session_state.user.get('name', ''))
            new_grid = st.text_input("Grid Square", value=st.session_state.user.get('grid_square', ''))
            new_email = st.text_input("Email", value=st.session_state.user.get('email', ''))
            new_phone = st.text_input("Phone", value=st.session_state.user.get('phone', ''))
            
            # Timezone selection
            import pytz
            common_timezones = [
                'UTC', 'US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific',
                'US/Alaska', 'US/Hawaii', 'Europe/London', 'Europe/Paris',
                'Asia/Tokyo', 'Australia/Sydney'
            ]
            current_tz = st.session_state.user.get('timezone', 'UTC')
            if current_tz not in common_timezones:
                common_timezones.append(current_tz)
            
            new_timezone = st.selectbox(
                "Timezone",
                options=common_timezones,
                index=common_timezones.index(current_tz) if current_tz in common_timezones else 0,
                help="Select your local timezone for displaying times"
            )
            
            if st.form_submit_button("Update Profile", width='stretch'):
                if db.update_user_settings(
                    st.session_state.user['callsign'],
                    name=new_name,
                    grid_square=new_grid.upper() if new_grid else None,
                    email=new_email if new_email else None,
                    phone=new_phone if new_phone else None,
                    timezone=new_timezone
                ):
                    # Update session state
                    st.session_state.user['name'] = new_name
                    st.session_state.user['grid_square'] = new_grid.upper() if new_grid else None
                    st.session_state.user['email'] = new_email if new_email else None
                    st.session_state.user['phone'] = new_phone if new_phone else None
                    st.session_state.user['timezone'] = new_timezone
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile")
    
    # Alert Settings
    with st.expander("🔔 Alert Settings", expanded=False):
        with st.form("alert_settings_form"):
            st.subheader("Configure Alerts & Notifications")
            
            sms_enabled = st.checkbox(
                "Enable SMS Alerts",
                value=st.session_state.user.get('sms_alerts_enabled', False),
                help="Receive SMS notifications for propagation alerts"
            )
            
            email_enabled = st.checkbox(
                "Enable Email Alerts",
                value=st.session_state.user.get('email_alerts_enabled', False),
                help="Receive email notifications for propagation alerts"
            )
            
            st.info("💡 **Coming Soon**: Configure specific alert triggers (band openings, rare DX, etc.)")
            
            if st.form_submit_button("Save Alert Settings", width='stretch'):
                if not st.session_state.user.get('phone') and sms_enabled:
                    st.error("Please add a phone number in Profile Settings first")
                elif not st.session_state.user.get('email') and email_enabled:
                    st.error("Please add an email address in Profile Settings first")
                else:
                    if db.update_user_settings(
                        st.session_state.user['callsign'],
                        sms_alerts_enabled=sms_enabled,
                        email_alerts_enabled=email_enabled
                    ):
                        st.session_state.user['sms_alerts_enabled'] = sms_enabled
                        st.session_state.user['email_alerts_enabled'] = email_enabled
                        st.success("Alert settings updated!")
                        st.rerun()
                    else:
                        st.error("Failed to update alert settings")
    
    st.divider()
    
    # Logout
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚪 Logout", type="secondary", width='stretch'):
            # Clear session from database
            db.clear_session_token(st.session_state.user['callsign'])
            # Clear cookie
            clear_auth_cookie()
            # Clear session state
            st.session_state.logged_in = False
            st.session_state.user = {}
            st.success("Logged out successfully")
            st.rerun()
