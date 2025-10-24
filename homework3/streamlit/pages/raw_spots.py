import streamlit as st
import requests
import pandas as pd

st.title("Raw DX Cluster Data")

# API URL
API_URL = "http://dx.jxqz.org:8080/api/spots?band=10m"

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

spots = fetch_spots()

if spots:
    df = pd.DataFrame(spots)
    st.dataframe(df)
else:
    st.write("No spots available.")