#!/usr/bin/env python3
#
# Initialize DX Cluster Database Schema in PostgreSQL
# Creates tables for storing DX spots with proper relationships

import os
import sys
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = 'dxcluster'
DB_USER = 'postgres'
DB_PASSWORD = None  # Using peer authentication for postgres user
DB_HOST = 'localhost'
DB_PORT = '5432'

def init_database():
    """Initialize the database with tables for DX cluster spots"""
    # Connection string
    conn_string = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Create table for storing raw DX spots
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_spots (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            raw_text TEXT NOT NULL
        )
        ''')

        # Create table for storing parsed DX spots
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dx_spots (
            id SERIAL PRIMARY KEY,
            raw_spot_id INTEGER REFERENCES raw_spots(id),
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            dx_call VARCHAR(20) NOT NULL,       -- Station being spotted
            frequency NUMERIC(10,3) NOT NULL,   -- Frequency in kHz
            spotter_call VARCHAR(20) NOT NULL,  -- Station making the spot
            comment TEXT,                       -- Any additional comments
            mode VARCHAR(10),                   -- Operating mode if specified
            signal_report VARCHAR(10),          -- Signal report if provided
            grid_square VARCHAR(6),             -- Grid square if provided
            band VARCHAR(10)                    -- Band (derived from frequency)
        )
        ''')

        # Create table for callsign information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS callsigns (
            id SERIAL PRIMARY KEY,
            callsign VARCHAR(20) UNIQUE NOT NULL,
            first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            total_spots INTEGER DEFAULT 0,
            total_spotted INTEGER DEFAULT 0
        )
        ''')

        # Create indices for better query performance
        # PostgreSQL automatically creates indices for PRIMARY KEY and UNIQUE constraints
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_timestamp ON dx_spots(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_frequency ON dx_spots(frequency)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_dx_call ON dx_spots(dx_call)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_spotter_call ON dx_spots(spotter_call)')
        
        # BRIN index might be more efficient for timestamp-based queries on large datasets
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dx_spots_timestamp_brin ON dx_spots USING brin(timestamp)')

        conn.commit()
        print(f"Successfully initialized database schema in PostgreSQL database '{DB_NAME}'")

    except (Exception, Error) as e:
        print(f"Error creating database schema: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    if not DB_PASSWORD:
        print("Error: Database password not set in environment variables", file=sys.stderr)
        sys.exit(1)

    print(f"Initializing DX cluster database in PostgreSQL database '{DB_NAME}'...")
    init_database()
    print("Database initialization complete.")

if __name__ == '__main__':
    main()