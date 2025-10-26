-- Migration: Add table for storing WWV propagation announcements (short format only)
-- WWV announcements contain basic solar data from NIST short format messages

-- Create table for WWV announcements (simplified for short format)
CREATE TABLE IF NOT EXISTS wwv_announcements (
    id SERIAL PRIMARY KEY,
    raw_announcement_id INTEGER REFERENCES raw_spots(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    raw_text TEXT NOT NULL,

    -- Basic solar data (from short format: SFI=102 A=5 K=1 SSN=0)
    solar_flux INTEGER,                    -- SFI (Solar Flux Index)
    a_index INTEGER,                       -- A-index (planetary)
    k_index INTEGER,                       -- K-index (planetary)
    sunspot_number INTEGER,                -- Sunspot number (SSN)

    -- Metadata
    announcement_type VARCHAR(20) DEFAULT 'WWV',  -- Type of announcement
    parsed_successfully BOOLEAN DEFAULT FALSE,    -- Whether parsing was successful

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_wwv_announcements_timestamp ON wwv_announcements(timestamp);
CREATE INDEX IF NOT EXISTS idx_wwv_announcements_parsed ON wwv_announcements(parsed_successfully);

-- Add comment to table
COMMENT ON TABLE wwv_announcements IS 'Stores WWV propagation announcements with basic solar data from short format messages';