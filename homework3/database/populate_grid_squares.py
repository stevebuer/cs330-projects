#!/usr/bin/env python3
"""
Populate the grid_squares lookup table with coordinate data from JSON file
"""

import json
import os
import sys
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv('DB_NAME', 'dx_analysis')
DB_USER = os.getenv('DB_USER', 'steve')
DB_PASSWORD = None  # Using peer authentication for postgres user
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

def populate_grid_squares(json_file='grid_squares.json'):
    """Populate the grid_squares table with data from JSON file"""

    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found. Run grid_utils.py first to generate it.")
        return False

    # Load grid square data
    print(f"Loading grid square data from {json_file}...")
    try:
        with open(json_file, 'r') as f:
            grid_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return False

    print(f"Found {len(grid_data)} grid squares to insert")

    # Connection string
    conn_string = f"dbname={DB_NAME} user={DB_USER}"

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Clear existing data (optional - comment out if you want to append)
        print("Clearing existing grid square data...")
        cursor.execute('DELETE FROM grid_squares')

        # Insert grid square data
        print("Inserting grid square coordinates...")
        inserted_count = 0

        for grid, coords in grid_data.items():
            if len(coords) >= 2:
                lat, lon = coords[0], coords[1]
                cursor.execute('''
                    INSERT INTO grid_squares (grid, lat, lon)
                    VALUES (%s, %s, %s)
                ''', (grid, lat, lon))
                inserted_count += 1

                # Progress indicator
                if inserted_count % 5000 == 0:
                    print(f"  Inserted {inserted_count} grid squares...")

        conn.commit()
        print(f"Successfully inserted {inserted_count} grid squares")

        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM grid_squares')
        count = cursor.fetchone()[0]
        print(f"Verification: {count} records in grid_squares table")

        return True

    except (Exception, Error) as e:
        print(f"Error populating grid squares table: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    # Default JSON file location
    json_file = 'grid-squares/grid_squares.json'

    # Check if custom file path provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    print(f"Populating grid_squares table from {json_file}")
    print(f"Database: {DB_NAME}")
    print()

    if populate_grid_squares(json_file):
        print("\nGrid squares lookup table populated successfully!")
        print("\nYou can now use queries like:")
        print("  SELECT lat, lon FROM grid_squares WHERE grid = 'FN42';")
        print("  SELECT * FROM grid_squares WHERE lat BETWEEN 40 AND 45;")
    else:
        print("\nFailed to populate grid squares table.")
        sys.exit(1)

if __name__ == '__main__':
    main()