#!/usr/bin/env python3
"""
Test script to verify grid_squares table population
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv('DB_NAME', 'dx_analysis')
DB_USER = os.getenv('DB_USER', 'steve')

def test_grid_squares_table():
    """Test that the grid_squares table has been populated correctly"""

    conn_string = f"dbname={DB_NAME} user={DB_USER}"

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Test 1: Check table exists and has data
        cursor.execute("SELECT COUNT(*) FROM grid_squares")
        count = cursor.fetchone()[0]
        print(f"✓ Grid squares table contains {count} records")

        if count == 0:
            print("✗ No data found in grid_squares table")
            return False

        # Test 2: Check some known grid squares
        test_grids = [
            ('FN42', 42.5, -71.0),    # Boston area
            ('EM12', 32.5, -97.0),    # Dallas area
            ('CN87', 47.5, -123.0),   # Seattle area
            ('AA00', -89.5, -179.0),  # South pole area
            ('RR99', 89.5, 179.0),    # North pole area
        ]

        print("\nTesting coordinate accuracy:")
        all_correct = True

        for grid, expected_lat, expected_lon in test_grids:
            cursor.execute("SELECT lat, lon FROM grid_squares WHERE grid = %s", (grid,))
            result = cursor.fetchone()

            if result:
                actual_lat, actual_lon = result
                lat_diff = abs(actual_lat - expected_lat)
                lon_diff = abs(actual_lon - expected_lon)

                if lat_diff < 0.01 and lon_diff < 0.01:  # Within 0.01 degrees
                    print(f"✓ {grid}: {actual_lat:.1f}, {actual_lon:.1f} ✓")
                else:
                    print(f"✗ {grid}: Expected ({expected_lat:.1f}, {expected_lon:.1f}), Got ({actual_lat:.1f}, {actual_lon:.1f})")
                    all_correct = False
            else:
                print(f"✗ {grid}: Not found in database")
                all_correct = False

        # Test 3: Check spatial query
        cursor.execute("""
            SELECT COUNT(*) FROM grid_squares
            WHERE lat BETWEEN 40 AND 50 AND lon BETWEEN -80 AND -60
        """)
        northeast_count = cursor.fetchone()[0]
        print(f"\n✓ Found {northeast_count} grid squares in Northeast US region")

        # Test 4: Check indices
        cursor.execute("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'grid_squares'
        """)
        indices = [row[0] for row in cursor.fetchall()]
        expected_indices = ['grid_squares_pkey', 'idx_grid_squares_lat', 'idx_grid_squares_lon']

        print(f"\n✓ Indices found: {', '.join(indices)}")
        for expected in expected_indices:
            if expected in indices:
                print(f"✓ Index {expected} exists")
            else:
                print(f"✗ Index {expected} missing")
                all_correct = False

        cursor.close()
        conn.close()

        return all_correct

    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

if __name__ == '__main__':
    print("Testing grid_squares table population...")
    print(f"Database: {DB_NAME}")
    print("-" * 50)

    if test_grid_squares_table():
        print("\n🎉 All tests passed! Grid squares table is properly populated.")
    else:
        print("\n❌ Some tests failed. Check the population script output.")