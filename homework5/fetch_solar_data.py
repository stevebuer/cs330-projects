#!/usr/bin/env python3
"""
Solar Data Fetcher for DX Dashboard
Fetches current solar conditions and stores in wwv_announcements table
Run from cron: */6 * * * * /path/to/fetch_solar_data.py
"""

import os
import sys
import psycopg2
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'dxcluster'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        sys.exit(1)

def fetch_solar_data_from_hamqsl():
    """
    Fetch solar data from hamqsl.com XML API
    Returns: dict with solar_flux, sunspot_number, a_index, k_index
    """
    try:
        url = "https://www.hamqsl.com/solarxml.php"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        data = {
            'solar_flux': None,
            'sunspot_number': None,
            'a_index': None,
            'k_index': None
        }
        
        # Extract values from XML
        solarflux = root.find('solarflux')
        if solarflux is not None and solarflux.text:
            data['solar_flux'] = int(solarflux.text)
        
        sunspots = root.find('sunspots')
        if sunspots is not None and sunspots.text:
            data['sunspot_number'] = int(sunspots.text)
        
        aindex = root.find('aindex')
        if aindex is not None and aindex.text:
            data['a_index'] = int(aindex.text)
        
        kindex = root.find('kindex')
        if kindex is not None and kindex.text:
            data['k_index'] = int(kindex.text)
        
        return data
        
    except requests.RequestException as e:
        print(f"Error fetching solar data from hamqsl.com: {e}", file=sys.stderr)
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None

def fetch_kindex_from_noaa():
    """
    Fetch current K-index from NOAA real-time endpoint
    Returns: dict with k_index
    """
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        # Skip header row, get most recent K-index
        if len(json_data) > 1:
            latest = json_data[-1]  # Most recent entry
            k_value = latest[1]  # K-index is second column
            return {'k_index': int(float(k_value))}
        
        return None
        
    except Exception as e:
        print(f"Error fetching K-index from NOAA: {e}", file=sys.stderr)
        return None

def fetch_solar_data_from_noaa():
    """
    Backup: Fetch solar data from NOAA JSON API
    Returns: dict with solar_flux, sunspot_number, a_index, k_index
    """
    try:
        url = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        # Get the most recent entry
        if json_data:
            latest = json_data[-1]
            data = {
                'solar_flux': int(latest.get('f10.7', 0)) if latest.get('f10.7') else None,
                'sunspot_number': int(latest.get('ssn', 0)) if latest.get('ssn') else None,
                'a_index': None,  # Not in this endpoint
                'k_index': None   # Not in this endpoint
            }
            return data
        
        return None
        
    except Exception as e:
        print(f"Error fetching from NOAA: {e}", file=sys.stderr)
        return None

def store_solar_data(conn, solar_data):
    """Store solar data in wwv_announcements table"""
    try:
        cursor = conn.cursor()
        
        # Create a synthetic raw_text entry for tracking
        timestamp = datetime.utcnow()
        raw_text = (f"Solar Data Update: SFI={solar_data['solar_flux']} "
                   f"SSN={solar_data['sunspot_number']} "
                   f"A={solar_data['a_index']} K={solar_data['k_index']}")
        
        # Insert into raw_spots first (for consistency with existing schema)
        cursor.execute('''
            INSERT INTO raw_spots (timestamp, raw_text)
            VALUES (%s, %s)
            RETURNING id
        ''', (timestamp, raw_text))
        raw_announcement_id = cursor.fetchone()[0]
        
        # Insert into wwv_announcements
        cursor.execute('''
            INSERT INTO wwv_announcements (
                raw_announcement_id, timestamp, raw_text,
                solar_flux, a_index, k_index, sunspot_number,
                announcement_type, parsed_successfully
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            raw_announcement_id,
            timestamp,
            raw_text,
            solar_data['solar_flux'],
            solar_data['a_index'],
            solar_data['k_index'],
            solar_data['sunspot_number'],
            'AUTO_FETCH',  # Mark as automated fetch
            True
        ))
        
        conn.commit()
        print(f"✓ Stored solar data: SFI={solar_data['solar_flux']}, "
              f"SSN={solar_data['sunspot_number']}, "
              f"A={solar_data['a_index']}, K={solar_data['k_index']}")
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error storing solar data: {e}", file=sys.stderr)
        return False
    finally:
        cursor.close()

def main():
    """Main execution"""
    print(f"Solar Data Fetcher - {datetime.utcnow().isoformat()}")
    
    # Try primary source (hamqsl.com)
    solar_data = fetch_solar_data_from_hamqsl()
    
    # Fallback to NOAA if hamqsl fails
    if not solar_data or not any(solar_data.values()):
        print("Trying backup source (NOAA)...")
        solar_data = fetch_solar_data_from_noaa()
    
    if not solar_data or not any(solar_data.values()):
        print("✗ Failed to fetch solar data from all sources", file=sys.stderr)
        sys.exit(1)
    
    # If K-index is missing, try to get it from NOAA real-time endpoint
    if solar_data.get('k_index') is None:
        print("Fetching K-index from NOAA...")
        k_data = fetch_kindex_from_noaa()
        if k_data and k_data.get('k_index') is not None:
            solar_data['k_index'] = k_data['k_index']
    
    # Connect to database and store
    conn = get_database_connection()
    try:
        success = store_solar_data(conn, solar_data)
        sys.exit(0 if success else 1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
