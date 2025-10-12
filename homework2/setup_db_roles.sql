-- Create roles for different components of the DX cluster system

-- Create group role for read-only access
CREATE ROLE dx_readonly WITH NOLOGIN;
GRANT CONNECT ON DATABASE dxcluster TO dx_readonly;
GRANT USAGE ON SCHEMA public TO dx_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dx_readonly;
-- Ensure future tables get the same grants
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dx_readonly;

-- Create group role for data ingestion
CREATE ROLE dx_writer WITH NOLOGIN;
GRANT CONNECT ON DATABASE dxcluster TO dx_writer;
GRANT USAGE ON SCHEMA public TO dx_writer;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO dx_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dx_writer;
-- Ensure future tables get the same grants
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT ON TABLES TO dx_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO dx_writer;

-- Create application roles that inherit from group roles

-- Web UI user - readonly access
CREATE USER dx_web_user WITH PASSWORD 'web_user_password_here' NOSUPERUSER;
GRANT dx_readonly TO dx_web_user;

-- DX Cluster scraper user - needs write access
CREATE USER dx_scraper WITH PASSWORD 'scraper_password_here' NOSUPERUSER;
GRANT dx_writer TO dx_scraper;

-- Personal admin user - full access
-- Replace 'steve' with your actual Linux username
CREATE USER steve WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE dxcluster TO steve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO steve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO steve;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO steve;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO steve;

-- Update the template for future tables
ALTER DEFAULT PRIVILEGES FOR ROLE steve IN SCHEMA public
GRANT SELECT ON TABLES TO dx_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE steve IN SCHEMA public
GRANT SELECT, INSERT ON TABLES TO dx_writer;