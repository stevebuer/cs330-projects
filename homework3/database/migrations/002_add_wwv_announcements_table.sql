-- Migration: Add table for storing WWV propagation announcements
-- WWV announcements contain solar and ionospheric data from NIST

-- Create table for WWV announcements
CREATE TABLE IF NOT EXISTS wwv_announcements (
    id SERIAL PRIMARY KEY,
    raw_announcement_id INTEGER REFERENCES raw_spots(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    raw_text TEXT NOT NULL,

    -- Solar data
    solar_flux INTEGER,                    -- SFI (Solar Flux Index)
    a_index INTEGER,                       -- A-index (planetary)
    k_index INTEGER,                       -- K-index (planetary)

    -- Sunspot data
    sunspot_number INTEGER,                -- Sunspot number (SSN)

    -- Ionospheric data
    xray_flux VARCHAR(10),                 -- X-ray flux level
    proton_flux VARCHAR(10),               -- Proton flux level

    -- Band conditions (typical ranges)
    band_80m VARCHAR(20),                  -- 80m band condition
    band_40m VARCHAR(20),                  -- 40m band condition
    band_30m VARCHAR(20),                  -- 30m band condition
    band_20m VARCHAR(20),                  -- 20m band condition
    band_17m VARCHAR(20),                  -- 17m band condition
    band_15m VARCHAR(20),                  -- 15m band condition
    band_12m VARCHAR(20),                  -- 12m band condition
    band_10m VARCHAR(20),                  -- 10m band condition

    -- Additional propagation data
    geomagnetic_storm VARCHAR(20),         -- Geomagnetic storm level
    solar_radiation_storm VARCHAR(20),     -- Solar radiation storm level

    -- Metadata
    announcement_type VARCHAR(20),         -- Type of announcement (WWV, WWVH, etc.)
    parsed_successfully BOOLEAN DEFAULT FALSE,  -- Whether parsing was successful

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_wwv_announcements_timestamp ON wwv_announcements(timestamp);
CREATE INDEX IF NOT EXISTS idx_wwv_announcements_parsed ON wwv_announcements(parsed_successfully);

-- Add comment to table
COMMENT ON TABLE wwv_announcements IS 'Stores WWV propagation announcements with solar and ionospheric data';