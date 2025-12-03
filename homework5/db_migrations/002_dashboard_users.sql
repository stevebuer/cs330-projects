-- User preferences table for Streamlit dashboard
CREATE TABLE IF NOT EXISTS dashboard_users (
    id SERIAL PRIMARY KEY,
    callsign VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    grid_square VARCHAR(6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_dashboard_users_callsign ON dashboard_users(callsign);

COMMENT ON TABLE dashboard_users IS 'User profiles and preferences for the DX dashboard';
COMMENT ON COLUMN dashboard_users.preferences IS 'JSON field for storing user-specific settings';
