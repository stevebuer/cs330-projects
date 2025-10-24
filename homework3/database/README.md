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

### 002_add_wwv_announcements_table.sql
Adds a `wwv_announcements` table to store WWV propagation announcements from NIST.

Table structure:
- `id`: Primary key
- `raw_announcement_id`: Foreign key to `raw_spots.id`
- `timestamp`: When the announcement was received
- `raw_text`: Full announcement text
- Solar data: `solar_flux`, `a_index`, `k_index`, `sunspot_number`
- Ionospheric data: `xray_flux`, `proton_flux`
- Band conditions: `band_80m` through `band_10m`
- Storm data: `geomagnetic_storm`, `solar_radiation_storm`
- `announcement_type`: Type of announcement (WWV, WWVH, etc.)
- `parsed_successfully`: Whether the data was successfully parsed

Includes indices on `timestamp` and `parsed_successfully` for performance.

**Note**: The DX cluster scraper (`scrapers/dx_cluster_live_pg.py`) has been updated to automatically detect and store WWV announcements.