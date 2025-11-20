# Database Migrations for Homework5

## Grafana Monitoring Role Setup

This document tracks database migrations and role setup for monitoring the production DX cluster database with Grafana.

### Prerequisites

- PostgreSQL superuser access
- Production database: `dx_analysis`
- Grafana instance installed and running

### Migration: Create Grafana Monitoring Role

**File:** `setup_grafana_db_role.sql`

**Purpose:** Create a read-only PostgreSQL role for Grafana to access database metrics and monitoring statistics without compromising security.

**What Gets Created:**
- `dx_monitoring` - Group role with read-only access to all tables and system statistics
- `dx_grafana` - Login user for Grafana with password-based authentication

**Permissions Granted:**
- SELECT on all tables in the public schema
- SELECT on PostgreSQL system statistics tables (`pg_stat_database`, `pg_stat_user_tables`, etc.)
- Access to information_schema and pg_catalog for system introspection

#### Execution Steps

1. **Update the password in the script:**
   
   Open `setup_grafana_db_role.sql` and replace `grafana_password_here` with a strong password:
   ```sql
   CREATE USER dx_grafana WITH PASSWORD 'YOUR_STRONG_PASSWORD' NOSUPERUSER NOCREATEDB;
   ```

2. **Apply the migration:**
   
   ```bash
   psql -U postgres -d dx_analysis -f setup_grafana_db_role.sql
   ```

3. **Verify the role was created:**
   
   ```bash
   psql -U postgres -d dx_analysis -c "\du dx_grafana"
   psql -U postgres -d dx_analysis -c "SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name='raw_spots';"
   ```

#### Grafana Data Source Configuration

Once the migration is applied, configure a PostgreSQL data source in Grafana:

- **Host:** your-database-hostname
- **Port:** 5432
- **Database:** dx_analysis
- **User:** dx_grafana
- **Password:** (the password you set above)
- **SSL Mode:** disable (or require based on your configuration)

#### Monitoring Capabilities

With this role, Grafana can monitor:
- Table row counts and sizes
- Index performance metrics
- Query statistics (if pg_stat_statements is enabled)
- Database connection counts
- Transaction activity
- DX spot ingestion rates

#### Rollback

To remove the Grafana monitoring role:

```sql
DROP USER IF EXISTS dx_grafana;
DROP ROLE IF EXISTS dx_monitoring;
```

---

## Future Migrations

- [ ] Time-series data retention policies
- [ ] Grafana dashboard definitions
- [ ] Alert rules for service failures
