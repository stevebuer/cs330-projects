#!/usr/bin/env python3
#
# Real-time DX Cluster Client with PostgreSQL Storage
# Connects to DX cluster via socket and stores spots in real-time
#

import socket
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
DB_NAME = os.getenv('DB_NAME', 'dx_analysis')
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

        # Extract grid squares if present in comment
        # Look for all Maidenhead grid locators (4-6 characters)
        grid_squares = re.findall(r'\b[A-R]{2}\d{2}[a-x]{2}?\b', comment.upper())
        
        # Assign grids based on count found
        dx_grid = None
        spotter_grid = None
        
        if len(grid_squares) >= 1:
            dx_grid = grid_squares[0]  # First grid is typically the DX station's
        if len(grid_squares) >= 2:
            spotter_grid = grid_squares[1]  # Second grid is typically the spotter's
        
        # For backward compatibility, keep the single grid_square field as dx_grid
        grid_square = dx_grid

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
            'grid_square': grid_square,  # For backward compatibility
            'dx_grid': dx_grid,          # DX station's grid
            'spotter_grid': spotter_grid, # Spotter's grid
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
            RETURNING id
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
        dx_spot_id = cursor.fetchone()[0]

        # Insert grid squares if both are available
        if spot_data.get('dx_grid') and spot_data.get('spotter_grid'):
            try:
                cursor.execute('''
                    INSERT INTO spot_grid_squares (dx_spot_id, source_grid, dest_grid)
                    VALUES (%s, %s, %s)
                ''', (dx_spot_id, spot_data['spotter_grid'], spot_data['dx_grid']))
            except psycopg2.Error as e:
                print(f"Error storing grid squares for spot {dx_spot_id}: {e}", file=sys.stderr)

        # Update callsign statistics
        update_callsign_stats(cursor, spot_data['spotter_call'], is_spotter=True)
        update_callsign_stats(cursor, spot_data['dx_call'], is_spotter=False)

        return True
    except psycopg2.Error as e:
        print(f"Database error storing spot: {e}", file=sys.stderr)
        return False

def connect_to_cluster(host, port, callsign):
    """Connect to DX cluster and return socket connection"""
    try:
        print(f"Connecting to {host}:{port}...")
        
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((host, port))
        
        # Wait for login prompt and send callsign
        print("Waiting for login prompt...")
        buffer = b""
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break
                buffer += data
                decoded = buffer.decode('utf-8', errors='ignore')
                print(f"Server: {decoded}")
                if 'login:' in decoded.lower() or 'call' in decoded.lower():
                    break
            except socket.timeout:
                break
        
        # Send callsign
        print(f"Sending callsign: {callsign}")
        sock.send(f"{callsign}\r\n".encode('ascii'))
        
        # Read initial messages
        time.sleep(2)
        try:
            sock.settimeout(2)  # Short timeout for initial messages
            buffer = b""
            for _ in range(10):  # Read up to 10 messages
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    buffer += data
                    decoded = buffer.decode('utf-8', errors='ignore')
                    lines = decoded.split('\n')
                    for line in lines[:-1]:  # All complete lines
                        if line.strip():
                            print(f"Server: {line.strip()}")
                    buffer = lines[-1].encode('utf-8')  # Keep incomplete line
                except socket.timeout:
                    break
        except:
            pass
        
        # Reset timeout for normal operation
        sock.settimeout(10)
        print("Connection established successfully!")
        
        return sock
        
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
    sock = connect_to_cluster(host, port, callsign)
    if not sock:
        sys.exit(1)

    spots_processed = 0
    lines_received = 0
    last_commit_time = time.time()
    buffer = b""  # Buffer for incomplete lines
    
    try:
        print("Monitoring DX spots... (storing to database)")
        print("-" * 60)
        
        while running:
            try:
                # Read data from socket connection
                data = sock.recv(1024)
                if not data:
                    print("Connection lost, attempting to reconnect...")
                    sock.close()
                    time.sleep(5)
                    sock = connect_to_cluster(host, port, callsign)
                    if not sock:
                        print("Failed to reconnect, exiting...")
                        break
                    buffer = b""
                    continue
                
                # Add new data to buffer
                buffer += data
                
                # Process complete lines
                while b'\n' in buffer:
                    line_bytes, buffer = buffer.split(b'\n', 1)
                    line = line_bytes.decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        continue
                    
                    lines_received += 1
                    
                    # Print all lines for monitoring
                    print(f"{datetime.utcnow().strftime('%H:%M:%S')} | {line}")
                    
                    # Check if this is a DX spot and parse it
                    if line.startswith('DX de '):
                        spot_data = parse_dx_spot_line(line)
                        if spot_data:
                            # Filter out frequencies above 54 MHz (54000 kHz)
                            if spot_data['frequency'] > 54000:
                                print(f"  -> Skipping spot: {spot_data['dx_call']} on {spot_data['frequency']} kHz (frequency too high)")
                                continue
                            
                            if store_spot(cursor, spot_data):
                                spots_processed += 1
                                grid_info = ""
                                if spot_data.get('dx_grid') and spot_data.get('spotter_grid'):
                                    grid_info = f" [{spot_data['spotter_grid']}->{spot_data['dx_grid']}]"
                                print(f"  -> Stored spot #{spots_processed}: {spot_data['dx_call']} on {spot_data['frequency']} by {spot_data['spotter_call']}{grid_info}")
                            
                            # Commit every 10 spots or every 60 seconds
                            current_time = time.time()
                            if spots_processed % 10 == 0 or (current_time - last_commit_time) > 60:
                                connection.commit()
                                last_commit_time = current_time
                                print(f"  -> Committed {spots_processed} spots to database")
                
            except socket.timeout:
                # Timeout is normal, just continue
                continue
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
            if sock:
                sock.close()
        except:
            pass

if __name__ == '__main__':
    main()
