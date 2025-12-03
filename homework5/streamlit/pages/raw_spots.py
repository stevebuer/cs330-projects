import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="Raw Spots", layout="wide")

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

st.title("📡 Raw DX Spot Data")

limit = st.number_input("Number of records", min_value=10, max_value=5000, value=100)

conn = get_db_connection()
if conn:
    query = """
    SELECT * FROM dx_spots
    ORDER BY timestamp DESC
    LIMIT %s
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(limit,))
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="dx_spots.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data available")
    except Exception as e:
        st.error(f"Query failed: {e}")
