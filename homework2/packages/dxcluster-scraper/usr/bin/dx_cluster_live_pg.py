#!/usr/bin/env python3
#
# Real-time DX Cluster Client with PostgreSQL Storage
# Connects to DX cluster via telnet and stores spots in real-time
#

import telnetlib
import psycopg2
import sys
import re
import os
import time
import signal
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DX Cluster server details
DEFAULT_HOST = 'dx.k3lr.com'
DEFAULT_PORT = 23
DEFAULT_CALLSIGN = 'N7MKO'

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'dxcluster')
DB_USER = os.getenv('DB_USER', 'dx_scraper')
DB_PASS = os.getenv('DB_PASSWORD', '')

# Global variables for graceful shutdown
running = True
connection = None
cursor = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running, connection, cursor
    print("\n\nShutting down gracefully...")
    running = False
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    sys.exit(0)

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def parse_dx_spot_line(line):
    """
    Parse a live DX spot line from telnet and return a dictionary of spot data
    Live format example: DX de IK8RJS:    14070.0  II8IARU      130th Radio 100th IARU PSK     1445Z
    """
    try:
        # Check if this is a DX spot line
        if not line.startswith('DX de '):
            return None

        # Add current timestamp since live feed doesn't include it
        current_timestamp = datetime.utcnow()
        
        # Create a formatted line similar to what the file parser expects
        formatted_line = f"{current_timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {line}"

        # Extract spotter callsign
        spotter_match = re.search(r'DX de ([A-Z0-9/-]+):', line)
        if not spotter_match:
            return None
        spotter_call = spotter_match.group(1)

        # Extract frequency, dx callsign and comments
        spot_pattern = r':\s*(\d+\.?\d*)\s+([A-Z0-9/-]+)\s*(.*?)\s*(\d{4}Z)?$'
        spot_match = re.search(spot_pattern, line)
        if not spot_match:
            return None

        frequency, dx_call, comment, utc = spot_match.groups()
        frequency = float(frequency)

        # Determine mode from comment if possible
        mode = None
        mode_indicators = {
            'CW': 'CW',
            'SSB': 'SSB',
            'LSB': 'LSB',
            'USB': 'USB',
            'FT8': 'FT8',
            'FT4': 'FT4',
            'PSK': 'PSK',
            'RTTY': 'RTTY'
        }
        for indicator, mode_type in mode_indicators.items():
            if indicator in comment.upper():
                mode = mode_type
                break

        # Determine band from frequency
        band = determine_band(frequency)

        # Extract grid square if present in comment
        grid_square = None
        grid_match = re.search(r'\b[A-R]{2}\d{2}[a-x]{2}\b', comment)
        if grid_match:
            grid_square = grid_match.group(0)

        # Extract signal report if present
        signal_report = None
        report_match = re.search(r'(?:[-+]\d+\s*[Dd][Bb]|5\d{1,2})', comment)
        if report_match:
            signal_report = report_match.group(0)

        return {
            'timestamp': current_timestamp,
            'raw_text': formatted_line.strip(),
            'dx_call': dx_call,
            'frequency': frequency,
            'spotter_call': spotter_call,
            'comment': comment.strip(),
            'mode': mode,
            'signal_report': signal_report,
            'grid_square': grid_square,
            'band': band
        }
    except Exception as e:
        print(f"Error parsing line: {line.strip()}", file=sys.stderr)
        print(f"Error details: {str(e)}", file=sys.stderr)
        return None

def determine_band(frequency):
    """Determine the amateur radio band based on frequency in kHz"""
    freq_ranges = {
        '2200m': (135.7, 137.8),
        '630m': (472.0, 479.0),
        '160m': (1800.0, 2000.0),
        '80m': (3500.0, 4000.0),
        '60m': (5351.5, 5366.5),
        '40m': (7000.0, 7300.0),
        '30m': (10100.0, 10150.0),
        '20m': (14000.0, 14350.0),
        '17m': (18068.0, 18168.0),
        '15m': (21000.0, 21450.0),
        '12m': (24890.0, 24990.0),
        '10m': (28000.0, 29700.0),
        '6m': (50000.0, 54000.0),
        '2m': (144000.0, 148000.0)
    }
    
    for band, (low, high) in freq_ranges.items():
        if low <= frequency <= high:
            return band
    return None

def update_callsign_stats(cursor, callsign, is_spotter=True):
    """Update the callsigns table statistics"""
    try:
        cursor.execute('''
            INSERT INTO callsigns (callsign, total_spots, total_spotted)
            VALUES (%s, %s, %s)
            ON CONFLICT(callsign) DO UPDATE SET
                last_seen = CURRENT_TIMESTAMP,
                total_spots = callsigns.total_spots + %s,
                total_spotted = callsigns.total_spotted + %s
        ''', (callsign, 1 if is_spotter else 0, 0 if is_spotter else 1,
              1 if is_spotter else 0, 0 if is_spotter else 1))
    except psycopg2.Error as e:
        print(f"Error updating callsign stats for {callsign}: {e}", file=sys.stderr)

def store_spot(cursor, spot_data):
    """Store a single DX spot in the database"""
    try:
        # Insert raw spot
        cursor.execute('''
            INSERT INTO raw_spots (timestamp, raw_text)
            VALUES (%s, %s)
            RETURNING id
        ''', (spot_data['timestamp'], spot_data['raw_text']))
        raw_spot_id = cursor.fetchone()[0]

        # Insert parsed spot
        cursor.execute('''
            INSERT INTO dx_spots (
                raw_spot_id, timestamp, dx_call, frequency,
                spotter_call, comment, mode, signal_report,
                grid_square, band
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            raw_spot_id,
            spot_data['timestamp'],
            spot_data['dx_call'],
            spot_data['frequency'],
            spot_data['spotter_call'],
            spot_data['comment'],
            spot_data['mode'],
            spot_data['signal_report'],
            spot_data['grid_square'],
            spot_data['band']
        ))

        # Update callsign statistics
        update_callsign_stats(cursor, spot_data['spotter_call'], is_spotter=True)
        update_callsign_stats(cursor, spot_data['dx_call'], is_spotter=False)

        return True
    except psycopg2.Error as e:
        print(f"Database error storing spot: {e}", file=sys.stderr)
        return False

def connect_to_cluster(host, port, callsign):
    """Connect to DX cluster and return telnet connection"""
    try:
        print(f"Connecting to {host}:{port}...")
        tn = telnetlib.Telnet(host, port, timeout=30)
        
        # Wait for login prompt and send callsign
        tn.read_until(b'login:', timeout=10)
        tn.write(f"{callsign}\r\n".encode('ascii'))
        
        # Read initial messages
        time.sleep(2)
        initial_data = tn.read_very_eager()
        if initial_data:
            print("Connection established. Initial response:")
            print(initial_data.decode('utf-8', errors='ignore'))
        
        return tn
    except Exception as e:
        print(f"Failed to connect to DX cluster: {e}", file=sys.stderr)
        return None

def main():
    global running, connection, cursor
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    callsign = DEFAULT_CALLSIGN
    
    if len(sys.argv) >= 2:
        callsign = sys.argv[1]
    if len(sys.argv) >= 3:
        host = sys.argv[2]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])

    print(f"DX Cluster Live Monitor - PostgreSQL Version")
    print(f"Callsign: {callsign}")
    print(f"Server: {host}:{port}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("Press Ctrl+C to stop\n")

    # Connect to database
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("Connected to PostgreSQL database")
    except psycopg2.Error as e:
        print(f"Failed to connect to database: {e}", file=sys.stderr)
        sys.exit(1)

    # Connect to DX cluster
    tn = connect_to_cluster(host, port, callsign)
    if not tn:
        sys.exit(1)

    spots_processed = 0
    lines_received = 0
    last_commit_time = time.time()
    
    try:
        print("Monitoring DX spots... (storing to database)")
        print("-" * 60)
        
        while running:
            try:
                # Read data from telnet connection
                data = tn.read_until(b'\n', timeout=10)
                if not data:
                    continue
                    
                line = data.decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                
                lines_received += 1
                
                # Print all lines for monitoring
                print(f"{datetime.utcnow().strftime('%H:%M:%S')} | {line}")
                
                # Check if this is a DX spot and parse it
                if line.startswith('DX de '):
                    spot_data = parse_dx_spot_line(line)
                    if spot_data:
                        if store_spot(cursor, spot_data):
                            spots_processed += 1
                            print(f"  -> Stored spot #{spots_processed}: {spot_data['dx_call']} on {spot_data['frequency']} by {spot_data['spotter_call']}")
                        
                        # Commit every 10 spots or every 60 seconds
                        current_time = time.time()
                        if spots_processed % 10 == 0 or (current_time - last_commit_time) > 60:
                            connection.commit()
                            last_commit_time = current_time
                            print(f"  -> Committed {spots_processed} spots to database")
                
            except Exception as e:
                if running:  # Only print error if we're not shutting down
                    print(f"Error processing data: {e}", file=sys.stderr)
                continue
                
    except KeyboardInterrupt:
        pass  # Handled by signal handler
    finally:
        try:
            if connection:
                connection.commit()
                print(f"\nFinal commit: {spots_processed} spots processed from {lines_received} total lines")
            tn.close()
        except:
            pass

if __name__ == '__main__':
    main()
