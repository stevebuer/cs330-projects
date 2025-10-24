#!/usr/bin/env python3
#
# Initialize RBN (Reverse Beacon Network) Database Schema in PostgreSQL
# Creates tables for storing CW beacon decodes from RBN

import os
import sys
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = 'dx_analysis'
DB_USER = 'postgres'
DB_PASSWORD = None  # Using peer authentication for postgres user
DB_HOST = 'localhost'
DB_PORT = '5432'

def init_rbn_database():
    """Initialize the database with tables for RBN CW beacon decodes"""
    # Connection string
    conn_string = f"dbname={DB_NAME} user={DB_USER}"

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Create table for storing raw RBN decodes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_rbn_decodes (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            raw_text TEXT NOT NULL
        )
        ''')

        # Create table for storing parsed RBN CW beacon decodes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rbn_cw_beacons (
            id SERIAL PRIMARY KEY,
            raw_decode_id INTEGER REFERENCES raw_rbn_decodes(id),
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            callsign VARCHAR(20) NOT NULL,      -- Station being decoded
            frequency NUMERIC(10,3) NOT NULL,   -- Frequency in kHz
            snr INTEGER,                        -- Signal-to-noise ratio in dB
            wpm INTEGER,                        -- CW speed in words per minute
            message TEXT,                       -- Decoded CW message
            band VARCHAR(10)                    -- Band (derived from frequency)
        )
        ''')

        # Create table for RBN callsign statistics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rbn_callsigns (
            id SERIAL PRIMARY KEY,
            callsign VARCHAR(20) UNIQUE NOT NULL,
            first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            total_decodes INTEGER DEFAULT 0,
            avg_snr NUMERIC(5,2),
            avg_wpm NUMERIC(5,2)
        )
        ''')

        # Create indices for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rbn_cw_beacons_timestamp ON rbn_cw_beacons(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rbn_cw_beacons_frequency ON rbn_cw_beacons(frequency)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rbn_cw_beacons_callsign ON rbn_cw_beacons(callsign)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rbn_cw_beacons_band ON rbn_cw_beacons(band)')

        conn.commit()
        print(f"Successfully initialized RBN database schema in PostgreSQL database '{DB_NAME}'")

    except (Exception, Error) as e:
        print(f"Error creating RBN database schema: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    print(f"Initializing RBN CW beacon database in PostgreSQL database '{DB_NAME}'...")
    init_rbn_database()
    print("RBN database initialization complete.")

if __name__ == '__main__':
    main()