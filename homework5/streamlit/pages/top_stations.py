import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="Top Stations", layout="wide")

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

st.title("🏆 Top Stations")

hours = st.slider("Time window (hours)", 1, 168, 24)
top_n = st.slider("Top N stations", 5, 50, 20)

conn = get_db_connection()
if conn:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Most Spotted DX Stations")
        query = """
        SELECT 
            dx_call,
            COUNT(*) as times_spotted,
            COUNT(DISTINCT spotter_call) as unique_spotters
        FROM dx_spots
        WHERE timestamp > NOW() - INTERVAL '%s hours'
        GROUP BY dx_call
        ORDER BY times_spotted DESC
        LIMIT %s
        """
        
        try:
            df = pd.read_sql_query(query, conn, params=(hours, top_n))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No data available")
        except Exception as e:
            st.error(f"Query failed: {e}")
    
    with col2:
        st.subheader("Most Active Spotters")
        query = """
        SELECT 
            spotter_call,
            COUNT(*) as spots_made,
            COUNT(DISTINCT dx_call) as unique_dx_spotted
        FROM dx_spots
        WHERE timestamp > NOW() - INTERVAL '%s hours'
        GROUP BY spotter_call
        ORDER BY spots_made DESC
        LIMIT %s
        """
        
        try:
            df = pd.read_sql_query(query, conn, params=(hours, top_n))
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No data available")
        except Exception as e:
            st.error(f"Query failed: {e}")
