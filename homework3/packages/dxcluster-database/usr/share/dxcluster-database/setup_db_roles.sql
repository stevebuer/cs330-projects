-- Database Role Setup for DX Cluster System
-- 
-- PRODUCTION DEPLOYMENT INSTRUCTIONS:
-- 1. Change all placeholder passwords before running in production
-- 2. Run this script AFTER creating the database schema (init_dx_database_pg.py)
-- 3. For existing databases, you may need to run the "Fix existing permissions" section separately
-- 4. Replace 'steve' with your actual admin username
--
-- Create roles for different components of the DX cluster system

-- Create group role for read-only access
DROP ROLE IF EXISTS dx_readonly;
CREATE ROLE dx_readonly WITH NOLOGIN;
GRANT CONNECT ON DATABASE dxcluster TO dx_readonly;
GRANT USAGE ON SCHEMA public TO dx_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dx_readonly;
-- Ensure future tables get the same grants
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dx_readonly;

-- Create group role for data ingestion
DROP ROLE IF EXISTS dx_writer;
CREATE ROLE dx_writer WITH NOLOGIN;
GRANT CONNECT ON DATABASE dxcluster TO dx_writer;
GRANT USAGE ON SCHEMA public TO dx_writer;
-- Grant permissions on existing tables
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO dx_writer;
-- Grant UPDATE specifically for callsigns table (needed for upsert operations)
GRANT UPDATE ON callsigns TO dx_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dx_writer;
-- Ensure future tables get the same grants
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO dx_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dx_writer;

-- Create application roles that inherit from group roles

-- Web UI user - readonly access
-- IMPORTANT: Change 'web_user_password_here' to a strong password for production
DROP USER IF EXISTS dx_web_user;
CREATE USER dx_web_user WITH PASSWORD 'web_user_password_here' NOSUPERUSER;
GRANT dx_readonly TO dx_web_user;

-- DX Cluster scraper user - needs write access
-- IMPORTANT: Change 'scraper_password_here' to a strong password for production
-- This should match the DB_PASSWORD in your .env file
DROP USER IF EXISTS dx_scraper;
CREATE USER dx_scraper WITH PASSWORD 'scraper_password_here' NOSUPERUSER;
GRANT dx_writer TO dx_scraper;

-- Personal admin user - full access
-- Replace 'steve' with your actual Linux username
DROP USER IF EXISTS steve;
CREATE USER steve WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE dxcluster TO steve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO steve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO steve;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO steve;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO steve;

-- Ensure that when ANY user creates tables, the proper permissions are granted
-- This covers cases where tables might be created by postgres, steve, or other users
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO dx_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO dx_writer;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dx_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dx_writer;

ALTER DEFAULT PRIVILEGES FOR ROLE steve IN SCHEMA public GRANT SELECT ON TABLES TO dx_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE steve IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO dx_writer;
ALTER DEFAULT PRIVILEGES FOR ROLE steve IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dx_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE steve IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dx_writer;

-- Grant UPDATE permission on callsigns table for future tables that follow the same pattern
-- Note: This is a workaround since we can't grant UPDATE on specific tables via default privileges
-- For production, you may need to manually grant UPDATE on the callsigns table after creation

-- ===================================================================
-- Fix permissions on existing tables (run this section if tables already exist)
-- ===================================================================

-- Grant proper permissions on existing tables
DO $$ 
BEGIN
    -- Check if tables exist and grant permissions
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'raw_spots') THEN
        GRANT SELECT, INSERT ON raw_spots TO dx_writer;
        GRANT SELECT ON raw_spots TO dx_readonly;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'dx_spots') THEN
        GRANT SELECT, INSERT ON dx_spots TO dx_writer;
        GRANT SELECT ON dx_spots TO dx_readonly;
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'callsigns') THEN
        GRANT SELECT, INSERT, UPDATE ON callsigns TO dx_writer;
        GRANT SELECT ON callsigns TO dx_readonly;
    END IF;
END $$;