import streamlit as st
import pydeck as pdk
import requests
import pandas as pd
import os

st.title("DX Cluster Map Visualization")

# API URL - from environment variable with fallback
API_URL = os.getenv("API_URL", "http://api.jxqz.org:8080/api/spots?band=10m")

# Function to fetch spots
def fetch_spots():
    try:
        response = requests.get(API_URL, verify=False)
        response.raise_for_status()
        data = response.json()
        return data.get('spots', [])
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# Function to convert Maidenhead grid to lat/lon
def maidenhead_to_latlon(grid):
    if not grid or len(grid) != 6:
        return None, None
    try:
        lon = (ord(grid[0].upper()) - ord('A')) * 20 - 180
        lat = (ord(grid[1].upper()) - ord('A')) * 10 - 90
        lon += int(grid[2]) * 2
        lat += int(grid[3])
        lon += (ord(grid[4].lower()) - ord('a')) * (2 / 24)
        lat += (ord(grid[5].lower()) - ord('a')) * (1 / 24)
        return lat, lon
    except:
        return None, None

spots = fetch_spots()

if spots:
    df = pd.DataFrame(spots)
    # Convert grid to lat/lon
    df[['lat', 'lon']] = df['grid_square'].apply(lambda x: pd.Series(maidenhead_to_latlon(x)))
    df = df.dropna(subset=['lat', 'lon'])
    
    if not df.empty:
        # Create PyDeck map
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            get_color=[200, 30, 0, 160],
            get_radius=50000,
            pickable=True,
        )
        
        view_state = pdk.ViewState(
            latitude=df['lat'].mean(),
            longitude=df['lon'].mean(),
            zoom=2,
            pitch=0,
        )
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{dx_call}\n{frequency}\n{mode}"},
        )
        
        st.pydeck_chart(deck)
    else:
        st.write("No valid grid squares to map.")
else:
    st.write("No spots available.")