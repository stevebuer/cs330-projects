#!/usr/bin/env python3
"""
One-time script to remove existing FT4 and FT8 mode spots from the database
"""

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

def cleanup_ft4_ft8_spots():
    """Remove all FT4 and FT8 mode spots from the database"""

    conn_string = f"dbname={DB_NAME} user={DB_USER}"

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print("Cleaning up FT4 and FT8 spots from database...")
        print(f"Database: {DB_NAME}")
        print("-" * 50)

        # First, find all FT4/FT8 spots
        cursor.execute("""
            SELECT COUNT(*) FROM dx_spots
            WHERE UPPER(mode) IN ('FT4', 'FT8')
        """)
        ft4_ft8_count = cursor.fetchone()[0]
        print(f"Found {ft4_ft8_count} FT4/FT8 spots to remove")

        if ft4_ft8_count == 0:
            print("No FT4/FT8 spots found. Nothing to clean up.")
            return True

        # Get the IDs of spots to delete for detailed logging
        cursor.execute("""
            SELECT id, dx_call, frequency, mode
            FROM dx_spots
            WHERE UPPER(mode) IN ('FT4', 'FT8')
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        sample_spots = cursor.fetchall()

        print("\nSample spots to be removed:")
        for spot in sample_spots:
            spot_id, dx_call, frequency, mode = spot
            print(f"  {mode}: {dx_call} on {frequency} kHz")

        if ft4_ft8_count > 10:
            print(f"  ... and {ft4_ft8_count - 10} more")

        # Confirm before deletion
        response = input(f"\nDelete {ft4_ft8_count} FT4/FT8 spots? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("Operation cancelled.")
            return False

        # Start transaction
        print("\nStarting cleanup...")

        # Skip spot_grid_squares deletion (table may not exist yet)
        print("ℹ Skipping spot_grid_squares cleanup (table may not exist yet)")
        grid_squares_deleted = 0

        # Step 2: Delete from dx_spots
        cursor.execute("""
            DELETE FROM dx_spots
            WHERE UPPER(mode) IN ('FT4', 'FT8')
        """)
        spots_deleted = cursor.rowcount
        print(f"✓ Deleted {spots_deleted} DX spot records")

        # Step 3: Optionally clean up orphaned raw_spots
        # Only delete raw_spots that are not referenced by remaining dx_spots or wwv_announcements
        cursor.execute("""
            DELETE FROM raw_spots
            WHERE id NOT IN (
                SELECT DISTINCT raw_spot_id FROM dx_spots
                UNION
                SELECT DISTINCT raw_announcement_id FROM wwv_announcements
            )
        """)
        raw_spots_deleted = cursor.rowcount
        print(f"✓ Deleted {raw_spots_deleted} orphaned raw spot records")

        # Commit the transaction
        conn.commit()

        print("\nCleanup completed successfully!")
        print(f"Total records removed: {grid_squares_deleted + spots_deleted + raw_spots_deleted}")

        # Verification
        cursor.execute("""
            SELECT COUNT(*) FROM dx_spots
            WHERE UPPER(mode) IN ('FT4', 'FT8')
        """)
        remaining = cursor.fetchone()[0]
        if remaining == 0:
            print("✓ Verification: No FT4/FT8 spots remaining")
        else:
            print(f"⚠ Warning: {remaining} FT4/FT8 spots still remain")

        return True

    except (Exception, Error) as e:
        print(f"Error during cleanup: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    print("FT4/FT8 Spot Cleanup Script")
    print("This will permanently remove all FT4 and FT8 mode spots from the database.")
    print()

    if cleanup_ft4_ft8_spots():
        print("\n🎉 Cleanup completed successfully!")
    else:
        print("\n❌ Cleanup failed or was cancelled.")
        exit(1)

if __name__ == '__main__':
    main()