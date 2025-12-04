#!/bin/bash
# Apply database migration for dashboard users table

echo "Applying dashboard users migration..."

# Check if .env file exists and source it
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Use environment variables or defaults
PGHOST=${PGHOST:-localhost}
PGPORT=${PGPORT:-5432}
PGDATABASE=${PGDATABASE:-dx_analysis}
PGUSER=${PGUSER:-steve}

echo "Connecting to: $PGDATABASE on $PGHOST:$PGPORT as $PGUSER"

#PGPASSWORD=$PGPASSWORD psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f db_migrations/002_dashboard_users.sql
psql -d "$PGDATABASE" -f 002_dashboard_users.sql

if [ $? -eq 0 ]; then
    echo "✓ Dashboard users table created successfully"
else
    echo "✗ Migration failed"
    exit 1
fi
