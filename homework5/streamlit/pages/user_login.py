import streamlit as st
import psycopg2
import os
from datetime import datetime

st.set_page_config(page_title="User Login", layout="centered")

DB_HOST = os.getenv('PGHOST', 'localhost')
DB_PORT = os.getenv('PGPORT', '5432')
DB_NAME = os.getenv('PGDATABASE', 'dx_analysis')
DB_USER = os.getenv('PGUSER', 'dx_web_user')
DB_PASSWORD = os.getenv('PGPASSWORD', '')

@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def save_user(callsign, name, grid_square):
    """Save or update user in database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dashboard_users (callsign, name, grid_square, last_login)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (callsign)
            DO UPDATE SET 
                name = EXCLUDED.name,
                grid_square = EXCLUDED.grid_square,
                last_login = NOW()
            RETURNING id, callsign, name, grid_square
        """, (callsign.upper(), name, grid_square.upper() if grid_square else None))
        
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        if result:
            return {
                'id': result[0],
                'callsign': result[1],
                'name': result[2],
                'grid_square': result[3]
            }
    except Exception as e:
        st.error(f"Error saving user: {e}")
        conn.rollback()
    
    return None

def get_user(callsign):
    """Retrieve user from database"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, callsign, name, grid_square
            FROM dashboard_users
            WHERE callsign = %s
        """, (callsign.upper(),))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'id': result[0],
                'callsign': result[1],
                'name': result[2],
                'grid_square': result[3]
            }
    except Exception as e:
        st.error(f"Error retrieving user: {e}")
    
    return None

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

st.title("👤 User Login")

if not st.session_state.logged_in:
    st.write("Enter your information to personalize your dashboard experience.")
    
    with st.form("login_form"):
        callsign = st.text_input("Callsign *", max_chars=20, help="Your amateur radio callsign")
        name = st.text_input("Name", max_chars=100, help="Your name (optional)")
        grid_square = st.text_input("Grid Square", max_chars=6, help="Your Maidenhead grid square (e.g., CN87)")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Login / Register", use_container_width=True)
        with col2:
            lookup = st.form_submit_button("Lookup Callsign", use_container_width=True)
        
        if lookup and callsign:
            existing_user = get_user(callsign)
            if existing_user:
                st.success(f"Found: {existing_user['name']} - {existing_user['grid_square']}")
                st.info("Click 'Login / Register' to log in with these details")
            else:
                st.warning(f"Callsign {callsign.upper()} not found. Fill in your details and click 'Login / Register'")
        
        if submit:
            if not callsign:
                st.error("Callsign is required!")
            else:
                user_data = save_user(callsign, name, grid_square)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.success(f"Welcome, {user_data['name'] or user_data['callsign']}!")
                    st.rerun()
else:
    st.success(f"✅ Logged in as: {st.session_state.user['callsign']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {st.session_state.user.get('name', 'Not set')}")
    with col2:
        st.write(f"**Grid:** {st.session_state.user.get('grid_square', 'Not set')}")
    
    st.divider()
    
    with st.form("update_form"):
        st.subheader("Update Your Information")
        new_name = st.text_input("Name", value=st.session_state.user.get('name', ''))
        new_grid = st.text_input("Grid Square", value=st.session_state.user.get('grid_square', ''))
        
        if st.form_submit_button("Update"):
            user_data = save_user(
                st.session_state.user['callsign'],
                new_name,
                new_grid
            )
            if user_data:
                st.session_state.user = user_data
                st.success("Profile updated!")
                st.rerun()
    
    st.divider()
    
    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user = {}
        st.rerun()
