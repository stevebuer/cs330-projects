#!/usr/bin/env python3
#
# Load DX cluster spots from a text file into PostgreSQL database
# Format: YYYY-MM-DD HH:MM:SS: DX de CALLER: FREQ.0 DXCALL COMMENTS UTCZ

import psycopg2
import sys
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'dx_analysis')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASSWORD', '')

DEFAULT_SPOTS_FILE = 'dx_spots.txt'

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def parse_spot(line):
    """
    Parse a DX spot line and return a dictionary of spot data
    Example line:
    2025-09-30 07:45:50: DX de IK8RJS:    14070.0  II8IARU      130th Radio 100th IARU PSK     1445Z
    """
    try:
        # Extract timestamp and rest of the line
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}): (.+)', line)
        if not timestamp_match:
            return None
            
        timestamp_str, spot_text = timestamp_match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        # Extract spotter callsign
        spotter_match = re.search(r'DX de ([A-Z0-9/-]+):', spot_text)
        if not spotter_match:
            return None
        spotter_call = spotter_match.group(1)

        # Extract frequency, dx callsign and comments
        # Use regex with named groups for better readability
        spot_pattern = r':\s*(\d+\.?\d*)\s+([A-Z0-9/-]+)\s*(.*?)\s*(\d{4}Z)?$'
        spot_match = re.search(spot_pattern, spot_text)
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
            'timestamp': timestamp,
            'raw_text': line.strip(),
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
    cursor.execute('''
        INSERT INTO callsigns (callsign, total_spots, total_spotted)
        VALUES (%s, %s, %s)
        ON CONFLICT(callsign) DO UPDATE SET
            last_seen = CURRENT_TIMESTAMP,
            total_spots = callsigns.total_spots + %s,
            total_spotted = callsigns.total_spotted + %s
    ''', (callsign, 1 if is_spotter else 0, 0 if is_spotter else 1,
          1 if is_spotter else 0, 0 if is_spotter else 1))

def load_spots(filename):
    """Load DX spots from file into database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    spots_processed = 0
    spots_skipped = 0
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                spot_data = parse_spot(line)
                if not spot_data:
                    spots_skipped += 1
                    continue

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

                spots_processed += 1
                if spots_processed % 100 == 0:
                    conn.commit()
                    print(f"Processed {spots_processed} spots...", file=sys.stderr)

        conn.commit()
        print(f"\nSpots processing complete:")
        print(f"Successfully processed: {spots_processed}")
        print(f"Skipped: {spots_skipped}")

    except psycopg2.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

def main():
    if len(sys.argv) > 1:
        spots_file = sys.argv[1]
    else:
        spots_file = DEFAULT_SPOTS_FILE
    
    print(f"Loading DX spots from {spots_file} into PostgreSQL database...")
    load_spots(spots_file)

if __name__ == '__main__':
    main()