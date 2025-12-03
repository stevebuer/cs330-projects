import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Propagation Trends", layout="wide")

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

st.title("📈 Propagation Trends")

hours = st.slider("Time window (hours)", 6, 168, 48)

conn = get_db_connection()
if conn:
    # Hourly spot counts
    query = """
    SELECT 
        DATE_TRUNC('hour', timestamp) as hour,
        COUNT(*) as spot_count,
        COUNT(DISTINCT dx_call) as unique_dx,
        COUNT(DISTINCT spotter_call) as unique_spotters
    FROM dx_spots
    WHERE timestamp > NOW() - INTERVAL '%s hours'
    GROUP BY hour
    ORDER BY hour
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(hours,))
        
        if not df.empty:
            st.subheader("Spot Activity Over Time")
            st.line_chart(df.set_index('hour')['spot_count'])
            
            st.subheader("Unique Stations")
            st.line_chart(df.set_index('hour')[['unique_dx', 'unique_spotters']])
            
            # Band activity over time
            st.subheader("Band Activity Over Time")
            band_query = """
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                band,
                COUNT(*) as count
            FROM dx_spots
            WHERE timestamp > NOW() - INTERVAL '%s hours'
                AND band IS NOT NULL
            GROUP BY hour, band
            ORDER BY hour, band
            """
            
            band_df = pd.read_sql_query(band_query, conn, params=(hours,))
            if not band_df.empty:
                pivot_df = band_df.pivot(index='hour', columns='band', values='count').fillna(0)
                st.line_chart(pivot_df)
            
            # Show raw data
            with st.expander("Show raw data"):
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("No data available")
    except Exception as e:
        st.error(f"Query failed: {e}")
