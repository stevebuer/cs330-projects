#!/usr/bin/env python3
#
# Reverse Beacon Network (RBN) Scraper for CW Beacons
# Connects to RBN telnet and stores CW decodes in database
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

# RBN server details
DEFAULT_HOST = 'rbn.telegraphy.de'
DEFAULT_PORT = 7000
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

def parse_rbn_line(line):
    """
    Parse a RBN line and return a dictionary of spot data
    RBN format example: 20231022 123456 28.0500 -23  23 dB  15 WPM  CQ N7MKO K
    """
    try:
        # RBN lines typically start with date/time
        # Format: YYYYMMDD HHMMSS frequency snr db wpm callsign message
        parts = line.strip().split()
        if len(parts) < 8:
            return None

        # Parse timestamp
        date_str = parts[0]
        time_str = parts[1]
        try:
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
        except ValueError:
            return None

        # Parse frequency
        try:
            frequency = float(parts[2]) * 1000  # Convert MHz to kHz
        except ValueError:
            return None

        # Skip if frequency is outside 10m band (28-29.7 MHz = 28000-29700 kHz)
        if not (28000 <= frequency <= 29700):
            return None

        # Parse SNR
        try:
            snr = int(parts[3])
        except ValueError:
            snr = None

        # Parse WPM
        wpm = None
        for i, part in enumerate(parts):
            if part.upper() == 'WPM':
                try:
                    wpm = int(parts[i-1])
                except (ValueError, IndexError):
                    pass
                break

        # Find callsign (usually after WPM)
        callsign = None
        message_start = None
        for i, part in enumerate(parts):
            if part.upper() == 'WPM' and i + 1 < len(parts):
                callsign = parts[i+1]
                message_start = i+2
                break

        if not callsign:
            return None

        # Extract message
        message = ' '.join(parts[message_start:]) if message_start else ''

        # Create raw text for storage
        raw_text = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: RBN {line.strip()}"

        # Determine band
        band = '10m'  # Since we're filtering for 10m

        return {
            'timestamp': timestamp,
            'raw_text': raw_text,
            'callsign': callsign,
            'frequency': frequency,
            'snr': snr,
            'wpm': wpm,
            'message': message,
            'band': band
        }
    except Exception as e:
        print(f"Error parsing RBN line: {line.strip()}", file=sys.stderr)
        print(f"Error details: {str(e)}", file=sys.stderr)
        return None

def update_callsign_stats(cursor, callsign):
    """Update the rbn_callsigns table statistics"""
    try:
        cursor.execute('''
            INSERT INTO rbn_callsigns (callsign, total_decodes)
            VALUES (%s, 1)
            ON CONFLICT(callsign) DO UPDATE SET
                last_seen = CURRENT_TIMESTAMP,
                total_decodes = rbn_callsigns.total_decodes + 1
        ''', (callsign,))
    except psycopg2.Error as e:
        print(f"Error updating RBN callsign stats for {callsign}: {e}", file=sys.stderr)

def store_rbn_decode(cursor, decode_data):
    """Store a single RBN CW decode in the database"""
    try:
        # Insert raw decode
        cursor.execute('''
            INSERT INTO raw_rbn_decodes (timestamp, raw_text)
            VALUES (%s, %s)
            RETURNING id
        ''', (decode_data['timestamp'], decode_data['raw_text']))
        raw_decode_id = cursor.fetchone()[0]

        # Insert parsed decode
        cursor.execute('''
            INSERT INTO rbn_cw_beacons (
                raw_decode_id, timestamp, callsign, frequency,
                snr, wpm, message, band
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            raw_decode_id,
            decode_data['timestamp'],
            decode_data['callsign'],
            decode_data['frequency'],
            decode_data['snr'],
            decode_data['wpm'],
            decode_data['message'],
            decode_data['band']
        ))

        # Update callsign statistics
        update_callsign_stats(cursor, decode_data['callsign'])

        return True
    except psycopg2.Error as e:
        print(f"Database error storing RBN decode: {e}", file=sys.stderr)
        return False

def connect_to_rbn(host, port, callsign):
    """Connect to RBN telnet and return socket connection"""
    try:
        print(f"Connecting to RBN at {host}:{port}...")

        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((host, port))

        # Wait for connection and send any initial commands if needed
        print("Connected to RBN, waiting for data...")
        time.sleep(2)

        # RBN doesn't require login like DX clusters, just starts sending data
        sock.settimeout(10)
        print("RBN connection established successfully!")

        return sock

    except Exception as e:
        print(f"Failed to connect to RBN: {e}", file=sys.stderr)
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

    print(f"RBN CW Beacon Monitor - PostgreSQL Version")
    print(f"Callsign: {callsign}")
    print(f"Server: {host}:{port}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("Monitoring 10m band CW beacons...")
    print("Press Ctrl+C to stop\n")

    # Connect to database
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("Connected to PostgreSQL database")
    except psycopg2.Error as e:
        print(f"Failed to connect to database: {e}", file=sys.stderr)
        sys.exit(1)

    # Connect to RBN
    sock = connect_to_rbn(host, port, callsign)
    if not sock:
        sys.exit(1)

    spots_processed = 0
    lines_received = 0
    last_commit_time = time.time()
    buffer = b""  # Buffer for incomplete lines

    try:
        print("Monitoring RBN CW decodes... (storing to database)")
        print("-" * 60)

        while running:
            try:
                # Read data from socket connection
                data = sock.recv(1024)
                if not data:
                    print("RBN connection lost, attempting to reconnect...")
                    sock.close()
                    time.sleep(5)
                    sock = connect_to_rbn(host, port, callsign)
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

                    # Parse RBN line
                    spot_data = parse_rbn_line(line)
                    if spot_data:
                        if store_rbn_decode(cursor, spot_data):
                            spots_processed += 1
                            print(f"  -> Stored RBN decode #{spots_processed}: {spot_data['callsign']} on {spot_data['frequency']} kHz (SNR: {spot_data['snr']}dB, WPM: {spot_data['wpm']})")

                        # Commit every 10 spots or every 60 seconds
                        current_time = time.time()
                        if spots_processed % 10 == 0 or (current_time - last_commit_time) > 60:
                            connection.commit()
                            last_commit_time = current_time
                            print(f"  -> Committed {spots_processed} RBN decodes to database")

            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except Exception as e:
                if running:  # Only print error if we're not shutting down
                    print(f"Error processing RBN data: {e}", file=sys.stderr)
                continue

    except KeyboardInterrupt:
        pass  # Handled by signal handler
    finally:
        try:
            if connection:
                connection.commit()
                print(f"\nFinal commit: {spots_processed} RBN decodes processed from {lines_received} total lines")
            if sock:
                sock.close()
        except:
            pass

if __name__ == '__main__':
    main()