-- Add password and settings fields to dashboard_users table
-- Migration: 003 - Add authentication and user settings

-- Add password hash column
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add email for notifications
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Add phone for SMS alerts
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- Add SMS alerts enabled flag
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS sms_alerts_enabled BOOLEAN DEFAULT FALSE;

-- Add email alerts enabled flag
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS email_alerts_enabled BOOLEAN DEFAULT FALSE;

-- Add session token for cookie-based auth
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS session_token VARCHAR(64);

-- Add session expiry
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS session_expires_at TIMESTAMP WITH TIME ZONE;

-- Add timezone preference
ALTER TABLE dashboard_users 
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';

-- Create index on session token for fast lookups
CREATE INDEX IF NOT EXISTS idx_dashboard_users_session_token ON dashboard_users(session_token);

-- Comments
COMMENT ON COLUMN dashboard_users.password_hash IS 'Bcrypt hashed password for authentication';
COMMENT ON COLUMN dashboard_users.email IS 'Email address for notifications and alerts';
COMMENT ON COLUMN dashboard_users.phone IS 'Phone number for SMS alerts (E.164 format recommended)';
COMMENT ON COLUMN dashboard_users.sms_alerts_enabled IS 'Whether user wants to receive SMS alerts';
COMMENT ON COLUMN dashboard_users.email_alerts_enabled IS 'Whether user wants to receive email alerts';
COMMENT ON COLUMN dashboard_users.session_token IS 'Secure token for cookie-based authentication';
COMMENT ON COLUMN dashboard_users.session_expires_at IS 'When the session token expires';
