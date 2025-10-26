# Database Migrations

This directory contains SQL migration files for the DX Analysis database.

## Production Deployment

For production server deployment instructions, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md).

## Migration Files

Migration files are named with a sequential number prefix (e.g., `001_`, `002_`) followed by a descriptive name and `.sql` extension.

## Running Migrations

To apply all pending migrations:

```bash
python run_migrations.py
```

The script will:
- Connect to the database specified by environment variables (or defaults)
- Execute migration files in alphabetical order
- Report success/failure for each migration

## Environment Variables

- `DB_NAME`: Database name (default: `dx_analysis`)
- `DB_USER`: Database user (default: `steve`)
- `DB_HOST`: Database host (default: `localhost`)
- `DB_PORT`: Database port (default: `5432`)

## Current Migrations

## Database Maintenance Scripts

### populate_grid_squares.py
Populates the `grid_squares` lookup table with coordinate data from the JSON file.

```bash
python database/populate_grid_squares.py
```

### cleanup_ft4_ft8.py
One-time script to remove existing FT4 and FT8 mode spots from the database.

**Warning**: This permanently deletes data. Use when you've added server-side filtering.

```bash
python database/cleanup_ft4_ft8.py
```

The script will:
- Show a count of spots to be removed
- Display sample spots for verification
- Ask for confirmation before deletion
- Skip `spot_grid_squares` cleanup (table may not exist if migrations not run)
- Remove records from `dx_spots` and orphaned `raw_spots` (includes `wwv_announcements` references)
- Provide verification that cleanup was successful

See [FT4_FT8_CLEANUP_README.md](FT4_FT8_CLEANUP_README.md) for detailed documentation.

### test_grid_squares.py
Verifies that the `grid_squares` table has been properly populated.

```bash
python database/test_grid_squares.py
```

## Usage Examples

### Basic Grid Lookup
```sql
-- Get coordinates for a specific grid
SELECT lat, lon FROM grid_squares WHERE grid = 'FN42';
```

### Distance Calculations
```sql
-- Calculate distance between two grids
SELECT
    g1.grid as grid1,
    g2.grid as grid2,
    ROUND(
        6371 * 2 * ASIN(SQRT(
            SIN(RADIANS(g2.lat - g1.lat)/2)^2 +
            COS(RADIANS(g1.lat)) * COS(RADIANS(g2.lat)) *
            SIN(RADIANS(g2.lon - g1.lon)/2)^2
        )), 1) as distance_km
FROM grid_squares g1, grid_squares g2
WHERE g1.grid = 'FN42' AND g2.grid = 'EM12';
```

### Spatial Queries
```sql
-- Find grids within a latitude range
SELECT grid, lat, lon
FROM grid_squares
WHERE lat BETWEEN 40 AND 45 AND lon BETWEEN -80 AND -70
ORDER BY lat, lon;
```

### Join with Propagation Data
```sql
-- Get propagation paths with coordinates
SELECT
    s.source_grid,
    s.dest_grid,
    g1.lat as source_lat,
    g1.lon as source_lon,
    g2.lat as dest_lat,
    g2.lon as dest_lon
FROM spot_grid_squares s
JOIN grid_squares g1 ON s.source_grid = g1.grid
JOIN grid_squares g2 ON s.dest_grid = g2.grid;
```