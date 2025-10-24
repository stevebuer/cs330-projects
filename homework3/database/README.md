# Database Migrations

This directory contains SQL migration files for the DX Analysis database.

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
- `DB_USER`: Database user (default: `postgres`)
- `DB_HOST`: Database host (default: `localhost`)
- `DB_PORT`: Database port (default: `5432`)

## Current Migrations

### 001_add_grid_squares_table.sql
Adds a `spot_grid_squares` table to store source (spotter) and destination (DX station) Maidenhead grid locators for DX spots that contain this information.

Table structure:
- `id`: Primary key
- `dx_spot_id`: Foreign key to `dx_spots.id`
- `source_grid`: Spotter's 4-6 character grid locator
- `dest_grid`: DX station's 4-6 character grid locator
- `created_at`: Timestamp when the record was created

Includes indices on `dx_spot_id`, `source_grid`, and `dest_grid` for performance.

**Note**: The DX cluster scraper (`scrapers/dx_cluster_live_pg.py`) has been updated to automatically populate this table when spots contain grid square information for both the spotter and DX station.