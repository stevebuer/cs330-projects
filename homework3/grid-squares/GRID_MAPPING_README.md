# Grid Square Mapping Utilities

This directory contains utilities for working with Maidenhead grid squares and mapping DX propagation paths.

## Files

### `grid_utils.py`
Core utilities for converting Maidenhead grid squares to latitude/longitude coordinates.

**Functions:**
- `grid_to_latlon(grid_square)`: Convert a single grid square to (lat, lon)
- `generate_grid_data(max_precision=4)`: Generate coordinate data for all valid grids
- `save_grid_data(filename, max_precision=4)`: Save grid data to JSON file

**Usage:**
```python
from grid_utils import grid_to_latlon, load_grid_data

# Convert single grid
lat, lon = grid_to_latlon('FN42')
print(f"FN42: {lat}, {lon}")  # FN42: 42.5, -71.0

# Load all grid data
grid_data = load_grid_data('grid_squares.json')
coords = grid_data.get('FN42')
```

### `grid_squares.json`
JSON file containing latitude/longitude coordinates for the center of all 32,400 valid 4-character Maidenhead grid squares.

**Format:**
```json
{
  "FN42": [42.5, -71.0],
  "EM12": [32.5, -97.0],
  ...
}
```

### `grid_mapping_demo.py`
Demonstration script showing how to use grid square coordinates for distance/bearing calculations.

**Features:**
- Load grid coordinate data
- Calculate distances between grid squares
- Calculate bearings between grid squares
- Example usage for mapping applications

### `generate_geojson.py`
Generate GeoJSON data for DX propagation paths that can be imported into mapping applications.

**Features:**
- Creates GeoJSON FeatureCollection with grid square markers and propagation paths
- Calculates distance and bearing for each path
- Compatible with Leaflet, Mapbox, QGIS, and other GIS tools

**Usage:**
```python
from generate_geojson import generate_propagation_geojson

# Generate GeoJSON for propagation paths
grid_pairs = [('FN42', 'EM12'), ('CN87', 'DM04')]
generate_propagation_geojson(grid_pairs, 'my_paths.geojson')
```

**GeoJSON Structure:**
- Point features for grid square locations
- LineString features for propagation paths
- Properties include distance, bearing, and grid codes

### `demo_propagation_paths.geojson`
Sample GeoJSON file showing propagation paths between major US cities.

**View in GIS Tools:**
- **QGIS**: Import as vector layer
- **Leaflet/Mapbox**: Load via JavaScript
- **Online Viewers**: geojson.io, geojson.tools

## Running the Examples

1. **Generate grid data:**
   ```bash
   python grid_utils.py
   ```

2. **Run mapping demo:**
   ```bash
   python grid_mapping_demo.py
   ```

3. **Generate GeoJSON for mapping:**
   ```bash
   python generate_geojson.py
   ```

## Integration with Database

Query the `spot_grid_squares` table and use the coordinates for analysis:

```sql
-- Get propagation data with coordinates
SELECT
    s.source_grid,
    s.dest_grid,
    g1.lat as source_lat,
    g1.lon as source_lon,
    g2.lat as dest_lat,
    g2.lon as dest_lon
FROM spot_grid_squares s
JOIN grid_squares g1 ON UPPER(s.source_grid) = g1.grid
JOIN grid_squares g2 ON UPPER(s.dest_grid) = g2.grid;
```

## Database Schema for Grid Squares

If you want to store coordinates directly in the database:

```sql
-- Add coordinates to spot_grid_squares table
ALTER TABLE spot_grid_squares
ADD COLUMN source_lat NUMERIC(8,4),
ADD COLUMN source_lon NUMERIC(9,4),
ADD COLUMN dest_lat NUMERIC(8,4),
ADD COLUMN dest_lon NUMERIC(9,4),
ADD COLUMN distance_km NUMERIC(8,2),
ADD COLUMN bearing_deg NUMERIC(5,1);

-- Populate coordinates (run once after migration)
UPDATE spot_grid_squares
SET
    source_lat = g1.lat,
    source_lon = g1.lon,
    dest_lat = g2.lat,
    dest_lon = g2.lon,
    distance_km = ROUND(
        6371 * 2 * ASIN(SQRT(
            SIN(RADIANS(g2.lat - g1.lat)/2)^2 +
            COS(RADIANS(g1.lat)) * COS(RADIANS(g2.lat)) *
            SIN(RADIANS(g2.lon - g1.lon)/2)^2
        )), 1),
    bearing_deg = ROUND(
        DEGREES(ATAN2(
            SIN(RADIANS(g2.lon - g1.lon)) * COS(RADIANS(g2.lat)),
            COS(RADIANS(g1.lat)) * SIN(RADIANS(g2.lat)) -
            SIN(RADIANS(g1.lat)) * COS(RADIANS(g2.lat)) * COS(RADIANS(g2.lon - g1.lon))
        )) + 360) % 360, 1)
FROM grid_squares g1, grid_squares g2
WHERE UPPER(source_grid) = g1.grid AND UPPER(dest_grid) = g2.grid;
```