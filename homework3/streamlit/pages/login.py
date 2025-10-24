import streamlit as st
import json

st.title("Login")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {}

if not st.session_state.logged_in:
    name = st.text_input("Name")
    callsign = st.text_input("Callsign")
    grid = st.text_input("Grid Square")
    
    if st.button("Login"):
        if name and callsign and grid:
            st.session_state.logged_in = True
            st.session_state.user = {'name': name, 'callsign': callsign, 'grid': grid}
            # Save to files
            with open('user_data.json', 'w') as f:
                json.dump(st.session_state.user, f)
            with open('login_state.json', 'w') as f:
                json.dump({'logged_in': True, 'user': st.session_state.user}, f)
            st.success("Logged in successfully! Go to the Home page.")
        else:
            st.error("Please fill in all fields.")
else:
    st.write("You are already logged in. Go to the Home page.")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = {}
        with open('login_state.json', 'w') as f:
            json.dump({'logged_in': False, 'user': {}}, f)
        st.rerun()