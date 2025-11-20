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
import logging
from datetime import datetime
from dotenv import load_dotenv
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
from prometheus_client import start_http_server
import threading

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

# Filtering configuration
SKIP_FT8_FREQUENCIES = os.getenv('SKIP_FT8_FREQUENCIES', 'true').lower() in ('true', '1', 'yes', 'on')

# Prometheus metrics configuration
METRICS_PORT = int(os.getenv('METRICS_PORT', '8000'))
METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() in ('true', '1', 'yes', 'on')

# Global variables for graceful shutdown
running = True
connection = None
cursor = None
verbose = False
debug = False

# Prometheus metrics
spots_total = Counter('dx_scraper_spots_total', 'Total DX spots received', ['band', 'mode'])
spots_stored = Counter('dx_scraper_spots_stored_total', 'Total DX spots successfully stored', ['band', 'mode'])
spots_filtered = Counter('dx_scraper_spots_filtered_total', 'Total DX spots filtered out', ['reason'])
wwv_total = Counter('dx_scraper_wwv_total', 'Total WWV announcements received')
wwv_stored = Counter('dx_scraper_wwv_stored_total', 'Total WWV announcements stored')
db_errors = Counter('dx_scraper_db_errors_total', 'Total database errors')
connection_errors = Counter('dx_scraper_connection_errors_total', 'Total connection errors')
lines_received = Gauge('dx_scraper_lines_received_total', 'Total lines received from cluster')
spots_received_gauge = Gauge('dx_scraper_spots_received', 'Spots received since last metric reset')
db_connection_time = Histogram('dx_scraper_db_insert_seconds', 'Database insert latency', buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0])
uptime = Gauge('dx_scraper_uptime_seconds', 'Scraper uptime in seconds')
last_spot_timestamp = Gauge('dx_scraper_last_spot_timestamp', 'Timestamp of last received spot')
cluster_connected = Gauge('dx_scraper_cluster_connected', 'Connection status to cluster (1=connected, 0=disconnected)')

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def setup_logging(verbose_mode, debug_mode):
    """Configure logging based on verbosity settings"""
    global logger
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    elif verbose_mode:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    """Handle Ctrl+C gracefully"""
    global running, connection, cursor
    logger.info("Shutting down gracefully...")
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
        logger.debug(f"Error parsing line: {line.strip()}")
        logger.debug(f"Error details: {str(e)}")
        return None

def parse_wwv_announcement(line):
    """
    Parse a WWV announcement line and return a dictionary of propagation data
    Focuses on short format messages: SFI=102 A=5 K=1 SSN=0
    """
    try:
        # Check if this is a WWV announcement
        if not (line.startswith('WWV de ') or 'WWV' in line.upper()):
            return None

        # Add current timestamp
        current_timestamp = datetime.utcnow()
        formatted_line = f"{current_timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {line}"

        # Initialize data structure (simplified for short format)
        wwv_data = {
            'timestamp': current_timestamp,
            'raw_text': formatted_line.strip(),
            'solar_flux': None,
            'a_index': None,
            'k_index': None,
            'sunspot_number': None,
            'announcement_type': 'WWV',
            'parsed_successfully': False
        }

        # Extract station callsign
        station_match = re.search(r'WWV de ([A-Z0-9/-]+):', line)
        if station_match:
            wwv_data['station_call'] = station_match.group(1)

        # Focus on short format: SFI=102 A=5 K=1 SSN=0
        sfi_match = re.search(r'SFI[=:](\d+)', line, re.IGNORECASE)
        if sfi_match:
            wwv_data['solar_flux'] = int(sfi_match.group(1))

        a_match = re.search(r'A[=:](\d+)', line, re.IGNORECASE)
        if a_match:
            wwv_data['a_index'] = int(a_match.group(1))

        k_match = re.search(r'K[=:](\d+)', line, re.IGNORECASE)
        if k_match:
            wwv_data['k_index'] = int(k_match.group(1))

        ssn_match = re.search(r'SSN[=:](\d+)', line, re.IGNORECASE)
        if ssn_match:
            wwv_data['sunspot_number'] = int(ssn_match.group(1))

        # If we found any key=value pairs, mark as successfully parsed
        if any([wwv_data['solar_flux'], wwv_data['a_index'], wwv_data['k_index'], wwv_data['sunspot_number']]):
            wwv_data['parsed_successfully'] = True

        return wwv_data

    except Exception as e:
        logger.debug(f"Error parsing WWV line: {line.strip()}")
        logger.debug(f"Error details: {str(e)}")
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

def is_ft8_frequency(frequency):
    """
    Check if a frequency is commonly used for FT8 or other digital modes.
    This includes standard FT8 calling frequencies and common digital mode segments.
    """
    # Common FT8 calling frequencies (exact matches)
    ft8_calling_freqs = {
        3573,   # 80m
        7074,   # 40m
        10136,  # 30m
        14074,  # 20m
        18100,  # 17m
        21074,  # 15m
        24915,  # 12m
        28074,  # 10m
        50313,  # 6m
    }
    
    # Check for exact FT8 calling frequency matches
    if int(frequency) in ft8_calling_freqs:
        return True
    
    # Common digital mode frequency ranges (where FT8 and other digital modes operate)
    digital_mode_ranges = [
        (3570, 3580),    # 80m digital segment
        (7070, 7080),    # 40m digital segment
        (10130, 10145),  # 30m digital segment
        (14070, 14080),  # 20m digital segment
        (18095, 18110),  # 17m digital segment
        (21070, 21080),  # 15m digital segment
        (24910, 24920),  # 12m digital segment
        (28070, 28085),  # 10m digital segment
        (50300, 50330),  # 6m digital segment
    ]
    
    # Check if frequency falls within digital mode ranges
    for low, high in digital_mode_ranges:
        if low <= frequency <= high:
            return True
    
    return False

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
        logger.debug(f"Error updating callsign stats for {callsign}: {e}")

def store_spot(cursor, spot_data):
    """Store a single DX spot in the database"""
    try:
        start_time = time.time()
        
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
                logger.debug(f"Error storing grid squares for spot {dx_spot_id}: {e}")

        # Update callsign statistics
        update_callsign_stats(cursor, spot_data['spotter_call'], is_spotter=True)
        update_callsign_stats(cursor, spot_data['dx_call'], is_spotter=False)

        # Record metrics
        db_connection_time.observe(time.time() - start_time)
        band = spot_data.get('band') or 'unknown'
        mode = spot_data.get('mode') or 'unknown'
        spots_stored.labels(band=band, mode=mode).inc()
        last_spot_timestamp.set(spot_data['timestamp'].timestamp())

        return True
    except psycopg2.Error as e:
        logger.debug(f"Database error storing spot: {e}")
        db_errors.inc()
        return False

def store_wwv_announcement(cursor, wwv_data):
    """Store a WWV announcement in the database (short format only)"""
    try:
        # Insert raw announcement (reuse raw_spots table for consistency)
        cursor.execute('''
            INSERT INTO raw_spots (timestamp, raw_text)
            VALUES (%s, %s)
            RETURNING id
        ''', (wwv_data['timestamp'], wwv_data['raw_text']))
        raw_announcement_id = cursor.fetchone()[0]

        # Insert parsed WWV data (simplified for short format)
        cursor.execute('''
            INSERT INTO wwv_announcements (
                raw_announcement_id, timestamp, raw_text,
                solar_flux, a_index, k_index, sunspot_number,
                announcement_type, parsed_successfully
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            raw_announcement_id,
            wwv_data['timestamp'],
            wwv_data['raw_text'],
            wwv_data['solar_flux'],
            wwv_data['a_index'],
            wwv_data['k_index'],
            wwv_data['sunspot_number'],
            wwv_data['announcement_type'],
            wwv_data['parsed_successfully']
        ))

        return True
    except psycopg2.Error as e:
        logger.debug(f"Database error storing WWV announcement: {e}")
        return False

def connect_to_cluster(host, port, callsign):
    """Connect to DX cluster and return socket connection"""
    try:
        logger.info(f"Connecting to {host}:{port}...")
        
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((host, port))
        
        # Wait for login prompt and send callsign
        logger.debug("Waiting for login prompt...")
        buffer = b""
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break
                buffer += data
                decoded = buffer.decode('utf-8', errors='ignore')
                logger.debug(f"Server: {decoded}")
                if 'login:' in decoded.lower() or 'call' in decoded.lower():
                    break
            except socket.timeout:
                break
        
        # Send callsign
        logger.debug(f"Sending callsign: {callsign}")
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
                            logger.debug(f"Server: {line.strip()}")
                    buffer = lines[-1].encode('utf-8')  # Keep incomplete line
                except socket.timeout:
                    break
        except:
            pass
        
        # Reset timeout for normal operation
        sock.settimeout(10)
        logger.info("Connection established successfully!")
        
        return sock
        
    except Exception as e:
        logger.error(f"Failed to connect to DX cluster: {e}")
        return None

def print_usage():
    """Print usage information"""
    print("DX Cluster Live Monitor - PostgreSQL Version")
    print("\nUsage: dx_cluster_live_pg.py [OPTIONS] [CALLSIGN] [HOST] [PORT]")
    print("\nOptions:")
    print("  -h, --help           Show this help message")
    print("  -v, --verbose        Enable verbose output")
    print("  -d, --debug          Enable debug output (includes all verbose)")
    print("\nPositional Arguments:")
    print("  CALLSIGN             Your callsign (default: N7MKO)")
    print("  HOST                 DX cluster host (default: dx.k3lr.com)")
    print("  PORT                 DX cluster port (default: 23)")
    print("\nExamples:")
    print("  dx_cluster_live_pg.py")
    print("  dx_cluster_live_pg.py N0CALL")
    print("  dx_cluster_live_pg.py -v N0CALL dx.k3lr.com 23")
    print("  dx_cluster_live_pg.py --debug N0CALL")

def main():
    global running, connection, cursor, verbose, debug
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    callsign = DEFAULT_CALLSIGN
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-h', '--help']:
            print_usage()
            sys.exit(0)
        elif arg in ['-v', '--verbose']:
            verbose = True
            i += 1
        elif arg in ['-d', '--debug']:
            debug = True
            verbose = True
            i += 1
        elif not arg.startswith('-'):
            # Positional arguments
            if i == len(sys.argv) - 3:
                callsign = arg
                host = sys.argv[i+1]
                port = int(sys.argv[i+2])
                break
            elif i == len(sys.argv) - 2:
                callsign = arg
                host = sys.argv[i+1]
                break
            elif i == len(sys.argv) - 1:
                callsign = arg
                break
            i += 1
        else:
            i += 1

    setup_logging(verbose, debug)

    print(f"DX Cluster Live Monitor - PostgreSQL Version")
    print(f"Callsign: {callsign}")
    print(f"Server: {host}:{port}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"FT8 Frequency Filtering: {'Enabled' if SKIP_FT8_FREQUENCIES else 'Disabled'}")
    if METRICS_ENABLED:
        print(f"Prometheus Metrics: Enabled (port {METRICS_PORT})")
    if verbose:
        print("Verbose mode: ENABLED")
    if debug:
        print("Debug mode: ENABLED")
    print("Press Ctrl+C to stop\n")

    # Start Prometheus metrics server
    start_metrics_server()

    # Connect to database
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        logger.info("Connected to PostgreSQL database")
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

    # Connect to DX cluster
    sock = connect_to_cluster(host, port, callsign)
    if not sock:
        sys.exit(1)

    cluster_connected.set(1)

    spots_received = 0
    wwv_received = 0
    lines_received_count = 0
    last_commit_time = time.time()
    start_time = time.time()
    buffer = b""  # Buffer for incomplete lines
    
    try:
        logger.info("Monitoring DX spots... (storing to database)")
        if not verbose and not debug:
            print("(Run with -v or --verbose for detailed output)")
        
        while running:
            try:
                # Update uptime
                uptime.set(time.time() - start_time)
                
                # Read data from socket connection
                data = sock.recv(1024)
                if not data:
                    logger.warning("Connection lost, attempting to reconnect...")
                    cluster_connected.set(0)
                    connection_errors.inc()
                    sock.close()
                    time.sleep(5)
                    sock = connect_to_cluster(host, port, callsign)
                    if not sock:
                        logger.error("Failed to reconnect, exiting...")
                        break
                    cluster_connected.set(1)
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
                    
                    lines_received_count += 1
                    lines_received.set(lines_received_count)
                    
                    # Print line if verbose mode is enabled
                    if verbose:
                        print(f"{datetime.utcnow().strftime('%H:%M:%S')} | {line}")
                    
                    # Check if this is a DX spot and parse it
                    if line.startswith('DX de '):
                        spot_data = parse_dx_spot_line(line)
                        if spot_data:
                            band = spot_data.get('band') or 'unknown'
                            mode = spot_data.get('mode') or 'unknown'
                            spots_total.labels(band=band, mode=mode).inc()
                            spots_received += 1
                            spots_received_gauge.set(spots_received)
                            
                            skip_reason = None
                            
                            # Filter out frequencies above 54 MHz (54000 kHz)
                            if spot_data['frequency'] > 54000:
                                skip_reason = "frequency_too_high"
                            
                            # Filter out 160m band spots
                            elif spot_data.get('band') == '160m':
                                skip_reason = "band_160m"
                            
                            # Filter out FT4 and FT8 spots based on mode detection
                            elif spot_data.get('mode') and spot_data['mode'].upper() in ['FT4', 'FT8']:
                                skip_reason = "mode_ft8_ft4"
                            
                            # Filter out spots on known FT8/digital mode frequencies if enabled
                            elif SKIP_FT8_FREQUENCIES and is_ft8_frequency(spot_data['frequency']):
                                skip_reason = "ft8_frequency"
                            
                            if skip_reason:
                                spots_filtered.labels(reason=skip_reason).inc()
                                logger.debug(f"Skipping spot: {spot_data['dx_call']} on {spot_data['frequency']} kHz ({skip_reason})")
                                continue
                            
                            if store_spot(cursor, spot_data):
                                grid_info = ""
                                if spot_data.get('dx_grid') and spot_data.get('spotter_grid'):
                                    grid_info = f" [{spot_data['spotter_grid']}->{spot_data['dx_grid']}]"
                                logger.info(f"Stored spot: {spot_data['dx_call']} on {spot_data['frequency']} by {spot_data['spotter_call']}{grid_info}")
                            
                            # Commit every 10 spots or every 60 seconds
                            current_time = time.time()
                            if spots_received % 10 == 0 or (current_time - last_commit_time) > 60:
                                connection.commit()
                                last_commit_time = current_time
                                logger.debug(f"Committed {spots_received} spots to database")
                    
                    # Check if this is a WWV announcement
                    elif 'WWV' in line.upper():
                        wwv_data = parse_wwv_announcement(line)
                        if wwv_data:
                            wwv_total.inc()
                            wwv_received += 1
                            
                            if store_wwv_announcement(cursor, wwv_data):
                                wwv_stored.inc()
                                status = "parsed" if wwv_data['parsed_successfully'] else "received"
                                logger.info(f"Stored WWV ({status}): SFI={wwv_data['solar_flux'] or 'N/A'} A={wwv_data['a_index'] or 'N/A'} K={wwv_data['k_index'] or 'N/A'}")
                            
                            # Commit every 5 WWV announcements or every 60 seconds
                            current_time = time.time()
                            if wwv_received % 5 == 0 or (current_time - last_commit_time) > 60:
                                connection.commit()
                                last_commit_time = current_time
                                logger.debug(f"Committed {wwv_received} WWV announcements to database")
                
            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except Exception as e:
                if running:  # Only print error if we're not shutting down
                    logger.error(f"Error processing data: {e}")
                continue
                
    except KeyboardInterrupt:
        pass  # Handled by signal handler
    finally:
        cluster_connected.set(0)
        try:
            if connection:
                connection.commit()
                logger.info(f"Final commit: {spots_received} spots and {wwv_received} WWV announcements processed from {lines_received_count} total lines")
            if sock:
                sock.close()
        except:
            pass

if __name__ == '__main__':
    main()
