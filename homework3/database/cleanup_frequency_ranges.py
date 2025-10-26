#!/usr/bin/env python3
"""
One-time script to remove DX spots outside the frequency range (7000-54000 kHz)
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

def cleanup_frequency_ranges():
    """Remove DX spots with frequencies outside 7000-54000 kHz range"""

    conn_string = f"dbname={DB_NAME} user={DB_USER}"

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print("Cleaning up DX spots outside frequency range (7000-54000 kHz)...")
        print(f"Database: {DB_NAME}")
        print("-" * 60)

        # Find all spots outside the frequency range
        cursor.execute("""
            SELECT COUNT(*) FROM dx_spots
            WHERE frequency < 7000 OR frequency > 54000
        """)
        out_of_range_count = cursor.fetchone()[0]
        print(f"Found {out_of_range_count} spots outside frequency range")

        if out_of_range_count == 0:
            print("No spots found outside frequency range. Nothing to clean up.")
            return True

        # Get the IDs of spots to delete for detailed logging
        cursor.execute("""
            SELECT id, dx_call, frequency, mode
            FROM dx_spots
            WHERE frequency < 7000 OR frequency > 54000
            ORDER BY frequency DESC
            LIMIT 10
        """)
        sample_spots = cursor.fetchall()

        print("\nSample spots to be removed:")
        for spot in sample_spots:
            spot_id, dx_call, frequency, mode = spot
            print(f"  {mode}: {dx_call} on {frequency} kHz")

        if out_of_range_count > 10:
            print(f"  ... and {out_of_range_count - 10} more")

        # Confirm before deletion
        response = input(f"\nDelete {out_of_range_count} out-of-range spots? (yes/no): ").lower().strip()
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
            WHERE frequency < 7000 OR frequency > 54000
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
            WHERE frequency < 7000 OR frequency > 54000
        """)
        remaining = cursor.fetchone()[0]
        if remaining == 0:
            print("✓ Verification: No out-of-range frequency spots remaining")
        else:
            print(f"⚠ Warning: {remaining} out-of-range frequency spots still remain")

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
    print("Frequency Range Cleanup Script")
    print("This will permanently remove all DX spots with frequencies < 7000 kHz or > 54000 kHz.")
    print()

    if cleanup_frequency_ranges():
        print("\n🎉 Cleanup completed successfully!")
    else:
        print("\n❌ Cleanup failed or was cancelled.")
        exit(1)

if __name__ == '__main__':
    main()