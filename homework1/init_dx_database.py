#!/usr/bin/env python3
#
# Initialize DX Cluster Database Schema
# Creates tables for storing DX spots with proper relationships

import sqlite3
import sys

# Database configuration
DB_NAME = 'dxcluster.db'

def init_database():
    """Initialize the database with tables for DX cluster spots"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # Create table for storing raw DX spots
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            raw_text TEXT NOT NULL
        )
        ''')

        # Create table for storing parsed DX spots
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dx_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_spot_id INTEGER,
            timestamp DATETIME NOT NULL,
            dx_call TEXT NOT NULL,       -- Station being spotted
            frequency REAL NOT NULL,     -- Frequency in kHz
            spotter_call TEXT NOT NULL,  -- Station making the spot
            comment TEXT,                -- Any additional comments
            mode TEXT,                   -- Operating mode if specified
            signal_report TEXT,          -- Signal report if provided
            grid_square TEXT,           -- Grid square if provided
            band TEXT,                  -- Band (derived from frequency)
            FOREIGN KEY (raw_spot_id) REFERENCES raw_spots(id)
        )
        ''')

        # Create table for callsign information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS callsigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            callsign TEXT UNIQUE NOT NULL,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_spots INTEGER DEFAULT 0,
            total_spotted INTEGER DEFAULT 0
        )
        ''')

        # Create indices for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_timestamp ON dx_spots(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_frequency ON dx_spots(frequency)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_dx_call ON dx_spots(dx_call)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_spotter_call ON dx_spots(spotter_call)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_callsigns_callsign ON callsigns(callsign)')

        conn.commit()
        print(f"Successfully initialized database schema in {DB_NAME}")

    except sqlite3.Error as e:
        print(f"Error creating database schema: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

def main():
    print(f"Initializing DX cluster database in {DB_NAME}...")
    init_database()
    print("Database initialization complete.")

if __name__ == '__main__':
    main()