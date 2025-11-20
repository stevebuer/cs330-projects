-- Grafana Monitoring Role Setup for Production Database
-- 
-- This script creates a read-only role for Grafana to access PostgreSQL
-- metrics and monitoring views without compromising security.
--
-- PRODUCTION DEPLOYMENT INSTRUCTIONS:
-- 1. Connect to your production PostgreSQL database as user steve (superuser)
-- 2. Change 'grafana_password_here' to a strong password
-- 3. Run: psql -U steve -d dx_analysis -f setup_grafana_db_role.sql
-- 4. Configure Grafana with the connection string:
--    postgresql://dx_grafana:PASSWORD@hostname:5432/dx_analysis
--

-- Drop existing user if it exists
DROP USER IF EXISTS dx_grafana;

-- Create group role for monitoring access (if it doesn't exist)
-- If it already exists, this will be skipped, and we just re-grant permissions
DO $$ 
BEGIN
    CREATE ROLE dx_monitoring WITH NOLOGIN;
EXCEPTION WHEN DUPLICATE_OBJECT THEN
    NULL;
END $$;

-- Grant permissions to the role
GRANT CONNECT ON DATABASE dx_analysis TO dx_monitoring;
GRANT USAGE ON SCHEMA public TO dx_monitoring;
GRANT USAGE ON SCHEMA information_schema TO dx_monitoring;
GRANT USAGE ON SCHEMA pg_catalog TO dx_monitoring;

-- Grant SELECT on system views for monitoring
-- Note: pg_stat_* are system views that provide database statistics
GRANT SELECT ON pg_stat_database TO dx_monitoring;
GRANT SELECT ON pg_stat_user_tables TO dx_monitoring;
GRANT SELECT ON pg_stat_user_indexes TO dx_monitoring;
GRANT SELECT ON pg_statio_user_tables TO dx_monitoring;
GRANT SELECT ON pg_statio_user_indexes TO dx_monitoring;

-- Grant SELECT on all existing tables (for DX cluster data monitoring)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dx_monitoring;
-- Ensure future tables are also readable
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dx_monitoring;

-- Create Grafana login user
-- IMPORTANT: Change 'grafana_password_here' to a strong password for production
CREATE USER dx_grafana WITH PASSWORD 'grafana_password_here' NOSUPERUSER NOCREATEDB;
GRANT dx_monitoring TO dx_grafana;

-- Verify permissions
-- Run as superuser to check:
-- SELECT grantee, privilege_type 
-- FROM information_schema.role_table_grants 
-- WHERE table_name='raw_spots' AND grantee='dx_monitoring';


