#!/usr/bin/env python3
#
# Run database migrations for the DX Analysis database
# Applies SQL migration files in order

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

def run_migration(migration_file):
    """Run a single migration file"""
    print(f"Running migration: {migration_file}")

    # Connection string
    conn_string = f"dbname={DB_NAME} user={DB_USER}"

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # Read and execute the migration file
        with open(migration_file, 'r') as f:
            sql = f.read()

        # Execute the SQL
        cursor.execute(sql)
        conn.commit()

        print(f"Successfully applied migration: {migration_file}")

    except (Exception, Error) as e:
        print(f"Error running migration {migration_file}: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return True

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    migrations_dir = os.path.join(script_dir, 'migrations')

    if not os.path.exists(migrations_dir):
        print(f"Migrations directory not found: {migrations_dir}", file=sys.stderr)
        sys.exit(1)

    # Get all .sql files in migrations directory, sorted by name
    migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
    migration_files.sort()

    if not migration_files:
        print("No migration files found.")
        return

    print(f"Found {len(migration_files)} migration file(s) to apply.")
    print(f"Database: {DB_NAME}")
    print()

    success_count = 0
    for migration_file in migration_files:
        migration_path = os.path.join(migrations_dir, migration_file)
        if run_migration(migration_path):
            success_count += 1
        else:
            print(f"Failed to apply migration: {migration_file}")
            break

    print()
    print(f"Applied {success_count} out of {len(migration_files)} migrations successfully.")

if __name__ == '__main__':
    main()