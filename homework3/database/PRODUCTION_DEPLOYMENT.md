# Production Database Deployment Guide

## Overview

This guide covers deploying the DX Analysis database to a production server environment.

## Environment Setup

### 1. Environment Variables

Create a `.env` file in the production environment using the provided template:

```bash
# Copy the example file
cp .env.example .env

# Edit with your production values
nano .env
```

Example `.env` file:
```bash
# Database Configuration
DB_NAME=dx_analysis
DB_USER=steve
DB_PASSWORD=your_production_password_here
DB_HOST=localhost
DB_PORT=5432
```

**Security Note**: Never commit `.env` files to version control. The `.env.example` file is safe to commit.

### 2. Database User Setup

On the production PostgreSQL server:

```sql
-- Create the database user (run as postgres superuser)
CREATE USER steve WITH PASSWORD 'your_secure_password';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE dx_analysis TO steve;

-- Create the database if it doesn't exist
CREATE DATABASE dx_analysis OWNER steve;
```

### 3. PostgreSQL Configuration

Ensure PostgreSQL is configured for password authentication:

**pg_hba.conf** (typically `/etc/postgresql/XX/main/pg_hba.conf`):
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   dx_analysis     steve                                   md5
host    dx_analysis     steve           127.0.0.1/32            md5
```

Restart PostgreSQL after configuration changes:
```bash
sudo systemctl restart postgresql
```

## Deployment Steps

### 1. Initial Database Setup

```bash
# Navigate to your project directory
cd /path/to/your/homework3

# Run migrations to create tables
python database/run_migrations.py
```

### 2. Populate Reference Data

```bash
# Load grid square coordinates (optional, for mapping features)
python database/populate_grid_squares.py
```

### 3. Data Cleanup (if needed)

If you have existing data that needs cleaning:

```bash
# Remove FT4/FT8 spots
python database/cleanup_ft4_ft8.py

# Remove out-of-range frequency spots
python database/cleanup_frequency_ranges.py
```

## Production Considerations

### Database Backups

**Automated Backups**:
```bash
# Create backup script
pg_dump -U steve -h localhost dx_analysis > dx_analysis_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -U steve -h localhost dx_analysis < backup_file.sql
```

### Monitoring

**Database Size**:
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Table Counts**:
```sql
SELECT
    'dx_spots' as table_name, COUNT(*) as count FROM dx_spots
UNION ALL
SELECT 'raw_spots', COUNT(*) FROM raw_spots
UNION ALL
SELECT 'wwv_announcements', COUNT(*) FROM wwv_announcements
UNION ALL
SELECT 'spot_grid_squares', COUNT(*) FROM spot_grid_squares
UNION ALL
SELECT 'grid_squares', COUNT(*) FROM grid_squares;
```

### Performance Tuning

**Recommended Indexes** (already included in migrations):
- `dx_spots`: timestamp, frequency, mode, band
- `wwv_announcements`: timestamp, parsed_successfully
- `spot_grid_squares`: dx_spot_id, source_grid, dest_grid

**Connection Pooling**: Consider using PgBouncer for high-traffic applications.

## Troubleshooting

### Connection Issues

**Test database connection**:
```bash
python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(f'dbname={os.getenv(\"DB_NAME\")} user={os.getenv(\"DB_USER\")} password={os.getenv(\"DB_PASSWORD\")}')
print('Connection successful')
conn.close()
"
```

### Migration Issues

**Check migration status**:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Re-run failed migrations**:
```bash
python database/run_migrations.py
```

### Data Issues

**Verify data integrity**:
```sql
-- Check for orphaned records
SELECT COUNT(*) as orphaned_raw_spots
FROM raw_spots
WHERE id NOT IN (
    SELECT DISTINCT raw_spot_id FROM dx_spots
    UNION
    SELECT DISTINCT raw_announcement_id FROM wwv_announcements
);
```

## Security Checklist

- [ ] Database user has strong password
- [ ] PostgreSQL configured for password authentication (not peer)
- [ ] `.env` file not committed to version control
- [ ] Database backups scheduled
- [ ] Minimal required permissions granted
- [ ] Network access restricted to necessary hosts
- [ ] SSL/TLS enabled for database connections

## Maintenance

### Regular Tasks

**Weekly**:
- Monitor database size growth
- Review error logs
- Verify backup integrity

**Monthly**:
- Analyze table statistics: `ANALYZE;`
- Reindex if needed: `REINDEX DATABASE dx_analysis;`
- Review and clean old data if necessary

### Log Rotation

Configure PostgreSQL log rotation in `postgresql.conf`:
```
log_rotation_age = 1d
log_rotation_size = 100MB
```

## Support

If you encounter issues:

1. Check the database logs: `/var/log/postgresql/`
2. Verify environment variables are set correctly
3. Test database connectivity
4. Review the troubleshooting section above
5. Check the detailed README files for each script