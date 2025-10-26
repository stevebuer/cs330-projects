-- Migration: Add table for storing Maidenhead grid square coordinates
-- Provides fast lookup of latitude/longitude for grid squares

-- Create table for grid square coordinates
CREATE TABLE IF NOT EXISTS grid_squares (
    grid VARCHAR(6) PRIMARY KEY,  -- Grid square code (4 or 6 characters)
    lat NUMERIC(8,4) NOT NULL,     -- Latitude in decimal degrees
    lon NUMERIC(9,4) NOT NULL      -- Longitude in decimal degrees
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_grid_squares_lat ON grid_squares(lat);
CREATE INDEX IF NOT EXISTS idx_grid_squares_lon ON grid_squares(lon);

-- Add comment to table
COMMENT ON TABLE grid_squares IS 'Maidenhead grid square coordinates for fast latitude/longitude lookup';