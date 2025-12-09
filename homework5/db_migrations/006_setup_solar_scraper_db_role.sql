-- Solar Data Scraper Database Role Setup
-- 
-- This script creates a database user for the solar data fetcher script with:
-- - INSERT access to wwv_announcements table (for storing solar data)
-- - INSERT access to raw_spots table (for consistency with WWV data storage)
-- - No SELECT or other permissions needed (write-only)
--
-- PRODUCTION DEPLOYMENT INSTRUCTIONS:
-- 1. Connect to your production PostgreSQL database as user steve (superuser)
-- 2. Change 'solar_scraper_password_here' to a strong password
-- 3. Run: psql -U steve -d dx_analysis -f 006_setup_solar_scraper_db_role.sql
-- 4. Update fetch_solar_data.py environment with: DB_USER=dx_solar_scraper
--

-- Drop existing user if it exists (for re-running this script)
DROP USER IF EXISTS dx_solar_scraper;

-- Create group role for solar data scraper (if it doesn't exist)
DO $$ 
BEGIN
    CREATE ROLE dx_solar_scraper_role WITH NOLOGIN;
EXCEPTION WHEN DUPLICATE_OBJECT THEN
    NULL;
END $$;

-- Grant database connection
GRANT CONNECT ON DATABASE dx_analysis TO dx_solar_scraper_role;
GRANT USAGE ON SCHEMA public TO dx_solar_scraper_role;

-- Grant INSERT and SELECT access to wwv_announcements table (for storing solar data)
GRANT SELECT, INSERT ON wwv_announcements TO dx_solar_scraper_role;
GRANT USAGE, SELECT ON SEQUENCE wwv_announcements_id_seq TO dx_solar_scraper_role;

-- Grant INSERT and SELECT access to raw_spots table (used by WWV storage mechanism)
GRANT SELECT, INSERT ON raw_spots TO dx_solar_scraper_role;
GRANT USAGE, SELECT ON SEQUENCE raw_spots_id_seq TO dx_solar_scraper_role;

-- Create the solar scraper login user
-- IMPORTANT: Change 'solar_scraper_password_here' to a strong password for production
CREATE USER dx_solar_scraper WITH PASSWORD 'solar_scraper_password_here' NOSUPERUSER NOCREATEDB;
GRANT dx_solar_scraper_role TO dx_solar_scraper;

-- Verify permissions
\echo 'Solar scraper user created: dx_solar_scraper'
\echo 'Permissions granted:'
\echo '  - SELECT, INSERT: wwv_announcements (for storing solar flux, K-index, etc.)'
\echo '  - SELECT, INSERT: raw_spots (for WWV announcement storage)'
\echo ''
\echo 'IMPORTANT: Update password before running in production!'
\echo 'Environment variables for fetch_solar_data.py:'
\echo '  DB_USER=dx_solar_scraper'
\echo '  DB_PASSWORD=your-password'
\echo '  DB_NAME=dx_analysis'
