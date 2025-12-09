-- Dashboard Database Role Setup for Production Database
-- 
-- This script creates a database user for the Streamlit dashboard with:
-- - READ access to all DX cluster data tables
-- - WRITE access only to dashboard_users table for authentication/preferences
--
-- PRODUCTION DEPLOYMENT INSTRUCTIONS:
-- 1. Connect to your production PostgreSQL database as user steve (superuser)
-- 2. Change 'dashboard_password_here' to a strong password
-- 3. Run: psql -U steve -d dx_analysis -f 005_setup_dashboard_db_role.sql
-- 4. Update .env file with: PGUSER=dx_dashboard and PGPASSWORD=your-password
--

-- Drop existing user if it exists (for re-running this script)
DROP USER IF EXISTS dx_dashboard;

-- Create group role for dashboard access (if it doesn't exist)
DO $$ 
BEGIN
    CREATE ROLE dx_dashboard_role WITH NOLOGIN;
EXCEPTION WHEN DUPLICATE_OBJECT THEN
    NULL;
END $$;

-- Grant database connection
GRANT CONNECT ON DATABASE dx_analysis TO dx_dashboard_role;
GRANT USAGE ON SCHEMA public TO dx_dashboard_role;

-- Grant READ access on all DX cluster data tables
GRANT SELECT ON dx_spots TO dx_dashboard_role;
GRANT SELECT ON raw_spots TO dx_dashboard_role;
GRANT SELECT ON callsigns TO dx_dashboard_role;
GRANT SELECT ON wwv_announcements TO dx_dashboard_role;
GRANT SELECT ON callsign_prefixes TO dx_dashboard_role;

-- Grant READ access to sequences for informational queries
GRANT SELECT ON SEQUENCE dx_spots_id_seq TO dx_dashboard_role;
GRANT SELECT ON SEQUENCE raw_spots_id_seq TO dx_dashboard_role;
GRANT SELECT ON SEQUENCE callsigns_id_seq TO dx_dashboard_role;

-- Grant FULL access to dashboard_users table (for authentication and user preferences)
GRANT SELECT, INSERT, UPDATE, DELETE ON dashboard_users TO dx_dashboard_role;
GRANT USAGE, SELECT ON SEQUENCE dashboard_users_id_seq TO dx_dashboard_role;

-- Ensure future tables created in public schema inherit permissions
-- (Read-only for new tables, except those explicitly granted write access)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dx_dashboard_role;

-- Create the dashboard login user
-- IMPORTANT: Change 'dashboard_password_here' to a strong password for production
CREATE USER dx_dashboard WITH PASSWORD 'dashboard_password_here' NOSUPERUSER NOCREATEDB;
GRANT dx_dashboard_role TO dx_dashboard;

-- Verify permissions
\echo 'Dashboard user created: dx_dashboard'
\echo 'Permissions granted:'
\echo '  - READ: dx_spots, raw_spots, callsigns, wwv_announcements, callsign_prefixes'
\echo '  - READ/WRITE: dashboard_users (for authentication and preferences)'
\echo ''
\echo 'IMPORTANT: Update password before running in production!'
\echo 'Connection string: postgresql://dx_dashboard:PASSWORD@hostname:5432/dx_analysis'
