# CS 330 Homework 3

Third iteration on DX Predictor Project.

## Todo List

* Another scraper data source
* Is there additional meta-data I need to create or extract to characterize a DX path?
	* Average, Max Distance propagated?
	* Observed MUF.
* Data Filtering: WSPR, Weaks signal crap ignore.
* Exclude 2 meter spots from DX cluster reports
* Create list of Steve's Personal Predictors (SPP) to watch
* Data mining? 
* What ML models can be developed?
* Add user login to Dash.
* Try another dashboard besides dash
* Sysadmin work to get space for container deploy
* Documentation on joins and join tables. Sqlite sample db for examples.
* Add automated test cases?
* Alerting infrastructure
* Configure AR-Cluster Filters: YAML FILE?
* Store WWV Reports

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
