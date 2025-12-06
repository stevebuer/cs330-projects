#!/usr/bin/env python3
"""
Load callsign prefix lookup table from JSON into PostgreSQL database.
This script reads callsign_countries.json and populates the callsign_prefixes table.
"""

import json
import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def get_db_connection():
    """Get PostgreSQL database connection from environment variables."""
    db_config = {
        'dbname': os.getenv('POSTGRES_DB', 'dx_cluster'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print(f"Connection config: {', '.join([f'{k}={v}' for k, v in db_config.items() if k != 'password'])}")
        sys.exit(1)

def load_json_data(json_path):
    """Load callsign prefix data from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['prefixes']
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except KeyError:
        print("Error: JSON file missing 'prefixes' key")
        sys.exit(1)

def create_table_if_not_exists(conn):
    """Create callsign_prefixes table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS callsign_prefixes (
        id SERIAL PRIMARY KEY,
        prefix VARCHAR(10) NOT NULL UNIQUE,
        country VARCHAR(255) NOT NULL,
        latitude DECIMAL(9, 6) NOT NULL,
        longitude DECIMAL(10, 6) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_callsign_prefixes_prefix ON callsign_prefixes(prefix);
    CREATE INDEX IF NOT EXISTS idx_callsign_prefixes_country ON callsign_prefixes(country);
    """
    
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
    conn.commit()
    print("✓ Table callsign_prefixes created/verified")

def load_prefixes(conn, prefixes_data):
    """Load callsign prefixes into database."""
    # Convert JSON data to list of tuples for bulk insert
    prefix_records = [
        (prefix, data['country'], data['lat'], data['lon'])
        for prefix, data in prefixes_data.items()
    ]
    
    # Clear existing data and insert new data
    with conn.cursor() as cur:
        # Get current count
        cur.execute("SELECT COUNT(*) FROM callsign_prefixes")
        existing_count = cur.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠ Deleting {existing_count} existing records...")
            cur.execute("DELETE FROM callsign_prefixes")
        
        # Bulk insert using execute_values for efficiency
        insert_sql = """
        INSERT INTO callsign_prefixes (prefix, country, latitude, longitude)
        VALUES %s
        ON CONFLICT (prefix) DO UPDATE SET
            country = EXCLUDED.country,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            updated_at = NOW()
        """
        
        execute_values(cur, insert_sql, prefix_records)
        
        # Get final count
        cur.execute("SELECT COUNT(*) FROM callsign_prefixes")
        final_count = cur.fetchone()[0]
        
    conn.commit()
    print(f"✓ Loaded {final_count} callsign prefixes into database")
    
    return final_count

def verify_data(conn):
    """Verify loaded data with sample queries."""
    with conn.cursor() as cur:
        # Count by continent/region
        print("\n📊 Sample data verification:")
        
        # Show some example prefixes
        cur.execute("""
            SELECT prefix, country, latitude, longitude 
            FROM callsign_prefixes 
            WHERE prefix IN ('K', 'G', 'JA', 'VK', 'PY', 'ZS')
            ORDER BY prefix
        """)
        
        print("\n  Example prefixes:")
        for row in cur.fetchall():
            print(f"    {row[0]:6s} - {row[1]:30s} ({row[2]:8.4f}, {row[3]:9.4f})")
        
        # Count total
        cur.execute("SELECT COUNT(*) FROM callsign_prefixes")
        total = cur.fetchone()[0]
        print(f"\n  Total prefixes in database: {total}")

def main():
    """Main function to load callsign prefixes."""
    # Determine paths
    script_dir = Path(__file__).parent
    json_path = script_dir / 'streamlit' / 'callsign_countries.json'
    
    print(f"Loading callsign prefixes from: {json_path}")
    
    # Load JSON data
    prefixes_data = load_json_data(json_path)
    print(f"✓ Loaded {len(prefixes_data)} prefixes from JSON file")
    
    # Connect to database
    print("\nConnecting to database...")
    conn = get_db_connection()
    print("✓ Database connection established")
    
    try:
        # Create table if needed
        create_table_if_not_exists(conn)
        
        # Load data
        print("\nLoading callsign prefixes into database...")
        count = load_prefixes(conn, prefixes_data)
        
        # Verify
        verify_data(conn)
        
        print("\n✅ Callsign prefix loading complete!")
        
    except Exception as e:
        print(f"\n❌ Error during loading: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
