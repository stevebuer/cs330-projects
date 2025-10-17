#!/bin/bash
# Production Database Setup Script for DX Cluster System
# 
# This script helps set up the database with proper security for production deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}DX Cluster Production Database Setup${NC}"
echo "====================================="

# Check if running as root (not recommended for production)
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}WARNING: Running as root is not recommended for production deployment${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo -e "${RED}ERROR: PostgreSQL is not running${NC}"
    echo "Start it with: sudo systemctl start postgresql"
    exit 1
fi

echo -e "${YELLOW}Step 1: Setting up database and schema${NC}"
echo "Make sure you have run init_dx_database_pg.py first to create tables"
read -p "Have you created the database schema? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please run: python3 init_dx_database_pg.py"
    exit 1
fi

echo -e "${YELLOW}Step 2: Password Configuration${NC}"
echo "You need to set strong passwords for the database users."

# Get admin user
read -p "Enter admin username (default: steve): " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-steve}

# Get passwords
echo "Enter password for dx_scraper user (used by the monitoring script):"
read -s SCRAPER_PASSWORD
echo

echo "Enter password for dx_web_user (used by web interface):"
read -s WEB_PASSWORD
echo

if [ -z "$SCRAPER_PASSWORD" ] || [ -z "$WEB_PASSWORD" ]; then
    echo -e "${RED}ERROR: Passwords cannot be empty${NC}"
    exit 1
fi

# Create temporary SQL file with actual passwords
TEMP_SQL=$(mktemp)
trap "rm -f $TEMP_SQL" EXIT

# Replace placeholders in the SQL file
sed -e "s/steve/$ADMIN_USER/g" \
    -e "s/scraper_password_here/$SCRAPER_PASSWORD/g" \
    -e "s/web_user_password_here/$WEB_PASSWORD/g" \
    setup_db_roles.sql > "$TEMP_SQL"

echo -e "${YELLOW}Step 3: Creating database roles and permissions${NC}"

# Run the SQL script
if psql -U "$ADMIN_USER" -d dxcluster -f "$TEMP_SQL"; then
    echo -e "${GREEN}✓ Database roles and permissions set up successfully${NC}"
else
    echo -e "${RED}✗ Failed to set up database roles${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 4: Updating .env file${NC}"
ENV_FILE=".env"

# Backup existing .env file
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backed up existing .env file"
fi

# Create/update .env file
cat > "$ENV_FILE" << EOF
# Database Configuration for DX Cluster
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dxcluster
DB_USER=dx_scraper
DB_PASSWORD=$SCRAPER_PASSWORD

# Uncomment and configure these for remote database access
#DB_HOST=your-database-host
#DB_PORT=5432

# Web user credentials (for web interface)
WEB_DB_USER=dx_web_user
WEB_DB_PASSWORD=$WEB_PASSWORD
EOF

echo -e "${GREEN}✓ .env file created/updated${NC}"

echo -e "${YELLOW}Step 5: Testing database connection${NC}"

# Test connection
if PGPASSWORD="$SCRAPER_PASSWORD" psql -h localhost -U dx_scraper -d dxcluster -c "SELECT 'Connection successful' as status;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connection test successful${NC}"
else
    echo -e "${RED}✗ Database connection test failed${NC}"
    echo "Check your PostgreSQL configuration and try again"
    exit 1
fi

echo
echo -e "${GREEN}Database setup completed successfully!${NC}"
echo
echo "Next steps:"
echo "1. Test your DX cluster monitor: python3 dx_cluster_live_pg.py"
echo "2. Set up web interface if needed"
echo "3. Configure firewall and security settings for production"
echo
echo -e "${YELLOW}Security reminders for production:${NC}"
echo "- Change default PostgreSQL port if exposed to internet"
echo "- Use SSL/TLS for database connections"
echo "- Regularly update passwords"
echo "- Monitor database logs"
echo "- Set up proper backup procedures"