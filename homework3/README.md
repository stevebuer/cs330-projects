# CS 330 Homework 3

Third iteration on DX Predictor Project.

## Done

* Created grid square lookup table. I want to be able to store information about the spotter and spottee location and the path between them possibly.
* Created new dashboard in Streamlit because it is a little simpler. I just need
this thing to work right now so I can integrate my ML models.
* Added [spot filtering](DX_CLUSTER_MACROS.md) on the DX cluster to limit some of the digital modes that are not relevant to my analysis such as FT8/FT4. Also, filtered out high and low ham bands that are not meaningful to me.
* Pruned some [old spots in the database](database/FREQUENCY_RANGE_CLEANUP_README.md) that were not relevant to analysis. Not sure if this cauased a problem or not yet.
* Expanded the schema to hold WWV solar data that I might like to add to my ML feature vector.
* Add ability to store WWV reports to DX cluster scraper.
* Created SQL study guide with Claude Haiku 4.5 (0.33x premium requests!) and a small sample database for query practice.
* Created LSTM model for propagation prediction. I need to test this.
* I am having some issues with the extract process from the API, need to debug.  
* Created a daily observation sheet that I will use for labeling training data. I need to listen to the radio mid day, or look at RF spectrum watefall visualization and label as good or bad propagation day for training.
* Deployment process: need to continue this!

## To Do

* Another scraper data source? RBN?
* Is there additional meta-data I need to create or extract to characterize a DX path?
	* Average, Max Distance propagated?
	* Observed MUF. 
* Create list of Steve's Personal Predictors (SPP) to watch
* Data mining? Unsupervised learning?
* Add user login to Das
* Documentation on joins and join tables. Sqlite sample db for examples.
* Add automated test cases?
* Alerting infrastructure?

## Store WWV Announcements in database

<pre>
   Date     Hour  SFI   A   K   Forecast
24-Oct-2025 00    130   6   2   No Storms -> No Storms                 <VE7CC>
23-Oct-2025 21    130   5   2   No Storms -> No Storms                 <AE5E>
23-Oct-2025 18    133   4   1   No Storms -> No Storms                 <W0MU>
23-Oct-2025 15    133   4   1   No Storms -> No Storms                 <VE7CC>
23-Oct-2025 12    133   4   1   No Storms -> No Storms                 <AE5E>
</pre>

## Done

### Namespace Adjustments

I renamed the database to reflect because I want to be able to bring in other data sources and other types of data such as user info.

*sudo systemctl stop dx-scraper*
<pre>
psql -d postgres
postgres=# ALTER DATABASE dxcluster RENAME TO dx_analysis;
</pre>
Update database name in /etc/dxcluster/dxcluster.env

*sudo systemctl start dx-scraper*

### Filter out FT4 and FT8

These are weak signal digital modes that people use even if the band is not open enough for voice communications. They are not useful indicators to me. I also created a script to delete
existing FT4 and FT8 scripts from the production DB.

### Filter out low bands and VHF

Todo

## Database Study

Postgres structure.

### Postgres Sequences

I have two.

## Maidenhead Grid Squares

Grid squares are in the format of XXnn e.g FN42 and describe a rectangle 1 degree by 2 degrees -- or 70 x 100 miles in the US.

I have loaded a table with all grids and their geographic center base on [grid-squares](grid-squares/GRID_MAPPING_README.md) info.

### Grid Squares Database Table

The `grid_squares` table provides fast lookup of latitude/longitude coordinates for all 32,400 valid 4-character Maidenhead grid squares.

**Setup:**
1. Run migration: `python database/run_migrations.py`
2. Populate data: `python database/populate_grid_squares.py`

**Usage:**
```sql
-- Get coordinates for Boston area
SELECT lat, lon FROM grid_squares WHERE grid = 'FN42';
-- Result: lat=42.5, lon=-71.0

-- Find grids in New England area
SELECT grid, lat, lon FROM grid_squares
WHERE lat BETWEEN 40 AND 45 AND lon BETWEEN -75 AND -65;
```

## Database Migrations

Ran the migrations:

<pre>
jersey% python3 run_migrations.py 
Found 3 migration file(s) to apply.
Database: dx_analysis

Running migration: /home/steve/GITHUB/cs330-projects/homework3/database/migrations/001_add_grid_squares_table.sql
Successfully applied migration: /home/steve/GITHUB/cs330-projects/homework3/database/migrations/001_add_grid_squares_table.sql
Running migration: /home/steve/GITHUB/cs330-projects/homework3/database/migrations/002_add_wwv_announcements_table.sql
Successfully applied migration: /home/steve/GITHUB/cs330-projects/homework3/database/migrations/002_add_wwv_announcements_table.sql
Running migration: /home/steve/GITHUB/cs330-projects/homework3/database/migrations/003_add_grid_squares_lookup_table.sql
Successfully applied migration: /home/steve/GITHUB/cs330-projects/homework3/database/migrations/003_add_grid_squares_lookup_table.sql

Applied 3 out of 3 migrations successfully.
</pre>

## Debian Package Infrastructure

The scraper dpkg infrastructure has been moved from homework2 to homework3 for unified deployment.

### Available Packages

**dxcluster-database**: Database schema and setup utilities
**dxcluster-scraper**: DX cluster monitoring service and management tools

### Building Packages

```bash
cd homework3
./build-packages.sh
```

### Package Management Scripts

- `manage-scraper.sh` - Service management (start/stop/restart/status/logs)
- `dx-scraper.service` - Systemd service definition for development

### Production Deployment

For production server deployment, see `database/PRODUCTION_DEPLOYMENT.md` and `packages/README.md`.

## API Container Infrastructure

The API container build infrastructure has been moved from homework2 to homework3 for unified deployment.

### Container Services

**dx-api**: Flask REST API server providing data access endpoints
- Built from `docker/Dockerfile.api`
- Runs on port 8080
- Health check endpoint: `/api/health`

**dx-dash**: Dash web dashboard for data visualization
- Built from `docker/Dockerfile.web`
- Runs on port 8050
- Health check endpoint: `/`

**dx-streamlit**: Streamlit interactive dashboard for DX propagation analysis
- Built from `docker/Dockerfile.streamlit`
- Runs on port 8501
- Health check endpoint: `/healthz`
- Features: Login system, multi-page navigation, real-time data analysis

### Docker Compose Configuration

Three compose files are available in the `docker/` directory:

- `docker/docker-compose.yml` - Development configuration with live building
- `docker/docker-compose.production.yml` - Production configuration with pre-built images
- `docker/docker-compose.production.simple.yml` - Simplified production setup

### Container Management

Use the `docker/docker-manage.sh` script for container operations:

```bash
cd docker

# Build and start services
./docker-manage.sh build
./docker-manage.sh start

# View logs and status
./docker-manage.sh logs
./docker-manage.sh status

# Stop services
./docker-manage.sh stop
```

### Environment Configuration

- `docker/.env.docker` - Template for Docker environment variables
- Requires PostgreSQL connection parameters (PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGPORT)

### Production Deployment

For production deployment with Traefik reverse proxy, use:

```bash
cd docker
./docker-manage.sh start-proxy
```

This enables access at:
- API: `http://api.dx.local`
- Dashboard: `http://dashboard.dx.local`
- Streamlit: `http://streamlit.dx.local`
- Traefik Dashboard: `http://localhost:8888`

## Data Cleanup Scripts

Created database cleanup utilities for maintaining data quality:

### FT4/FT8 Mode Removal

```bash
python database/cleanup_ft4_ft8.py
```

Removes all existing FT4 and FT8 mode spots from the database, including orphaned records.

### Frequency Range Filtering

```bash
python database/cleanup_frequency_ranges.py
```

Removes spots with frequencies outside 7000-54000 kHz range (below 40m and above 6m).