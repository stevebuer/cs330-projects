-- Migration: Add table for storing source and destination grid square locators
-- for DX cluster spots that contain grid square information

-- Create table for spot grid squares
CREATE TABLE IF NOT EXISTS spot_grid_squares (
    id SERIAL PRIMARY KEY,
    dx_spot_id INTEGER REFERENCES dx_spots(id) ON DELETE CASCADE,
    source_grid VARCHAR(6) NOT NULL,  -- Spotter's Maidenhead grid locator
    dest_grid VARCHAR(6) NOT NULL,    -- DX station's Maidenhead grid locator
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dx_spot_id)  -- Ensure one entry per DX spot
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_spot_grid_squares_dx_spot_id ON spot_grid_squares(dx_spot_id);
CREATE INDEX IF NOT EXISTS idx_spot_grid_squares_source_grid ON spot_grid_squares(source_grid);
CREATE INDEX IF NOT EXISTS idx_spot_grid_squares_dest_grid ON spot_grid_squares(dest_grid);

-- Add comment to table
COMMENT ON TABLE spot_grid_squares IS 'Stores source (spotter) and destination (DX) grid square locators for DX spots that contain this information';