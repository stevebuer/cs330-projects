#!/bin/bash
# Apply authentication migration to add password and settings support

cd "$(dirname "$0")"

echo "🔐 Applying Authentication Migration"
echo ""

# Load environment if .env exists
if [ -f "../streamlit/.env" ]; then
    export $(cat ../streamlit/.env | grep -v '^#' | xargs)
fi

DB_NAME=${PGDATABASE:-dx_analysis}
DB_USER=${PGUSER:-dx_web_user}
DB_HOST=${PGHOST:-localhost}
DB_PORT=${PGPORT:-5432}

echo "Applying migration to: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""

# Apply migration
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f 003_add_authentication.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Authentication migration applied successfully!"
    echo ""
    echo "New features enabled:"
    echo "  - Password-based authentication"
    echo "  - Persistent sessions via cookies"
    echo "  - Email and phone number storage"
    echo "  - SMS and email alert preferences"
    echo ""
    echo "Users will need to register new accounts with passwords."
else
    echo ""
    echo "✗ Migration failed. Please check database connection and permissions."
    exit 1
fi
