import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="Band Analysis", layout="wide")

# Database connection
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

st.title("📊 Band Analysis")

hours = st.slider("Time window (hours)", 1, 48, 12)

conn = get_db_connection()
if conn:
    query = """
    SELECT band, COUNT(*) as count
    FROM dx_spots
    WHERE timestamp > NOW() - INTERVAL '%s hours'
    GROUP BY band
    ORDER BY count DESC
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(hours,))
        
        if not df.empty:
            st.bar_chart(df.set_index('band'))
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No data available")
    except Exception as e:
        st.error(f"Query failed: {e}")
