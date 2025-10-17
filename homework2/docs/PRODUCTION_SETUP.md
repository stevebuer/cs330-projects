# Production Database Setup - Changes and Instructions

## What Was Fixed

The original `setup_db_roles.sql` had several issues that would cause problems in production:

### 1. Missing Permissions
- **Issue**: The script didn't grant UPDATE permission on the `callsigns` table
- **Fix**: Added explicit `GRANT UPDATE ON callsigns TO dx_writer;`
- **Why needed**: Your application uses `ON CONFLICT ... DO UPDATE` for upsert operations

### 2. Incomplete Default Privileges 
- **Issue**: Default privileges only covered tables created in the future, not existing ones
- **Fix**: Added a conditional block to grant permissions on existing tables
- **Why needed**: Prevents the "permission denied" error you experienced

### 3. Missing Safety Features
- **Issue**: No error handling for existing users/roles
- **Fix**: Added `DROP ROLE IF EXISTS` and `DROP USER IF EXISTS` statements
- **Why needed**: Allows script to be re-run safely during deployment

### 4. Inadequate Multi-User Coverage
- **Issue**: Default privileges only covered tables created by the current user
- **Fix**: Added default privileges for both `postgres` and `steve` roles
- **Why needed**: Ensures permissions work regardless of who creates tables

## Files Created/Modified

### 1. Updated `setup_db_roles.sql`
- ✅ Added production deployment instructions
- ✅ Fixed all permission issues
- ✅ Added error handling and safety features
- ✅ Added section for existing database fixes

### 2. New `setup_production_db.sh`
- ✅ Interactive script for secure password management
- ✅ Automatically updates `.env` file with correct credentials
- ✅ Tests database connectivity
- ✅ Provides production security reminders

### 3. New `.env.production.template`
- ✅ Complete configuration template for production
- ✅ Includes SSL/TLS settings for remote databases
- ✅ Performance tuning parameters
- ✅ Security best practices

## Production Deployment Steps

### For New Production Environment:

1. **Prepare the server:**
   ```bash
   # Install PostgreSQL and Python dependencies
   sudo apt update
   sudo apt install postgresql postgresql-contrib python3-pip
   pip3 install -r requirements-pg.txt
   ```

2. **Create the database:**
   ```bash
   # As postgres user, create database
   sudo -u postgres createdb dxcluster
   
   # Run schema creation
   python3 init_dx_database_pg.py
   ```

3. **Set up roles and permissions:**
   ```bash
   # Use the interactive setup script (recommended)
   ./setup_production_db.sh
   
   # OR manually edit setup_db_roles.sql and run:
   # psql -U postgres -d dxcluster -f setup_db_roles.sql
   ```

4. **Test the setup:**
   ```bash
   python3 dx_cluster_live_pg.py YOUR_CALLSIGN
   ```

### For Existing Development Database (like yours):

Your database already works because we manually fixed the permissions. To ensure it's production-ready:

1. **Update your setup script:**
   ```bash
   # Re-run the updated setup script to ensure all permissions are correct
   ./setup_production_db.sh
   ```

2. **Backup and update passwords:**
   ```bash
   # Change the default passwords
   psql -U steve -d dxcluster -c "ALTER USER dx_scraper PASSWORD 'new_strong_password';"
   psql -U steve -d dxcluster -c "ALTER USER dx_web_user PASSWORD 'another_strong_password';"
   ```

## Security Best Practices for Production

1. **Database Security:**
   - Change all default passwords to strong, unique values
   - Use SSL/TLS for database connections
   - Restrict network access to database server
   - Regularly rotate passwords

2. **Application Security:**
   - Store `.env` file with restricted permissions (600)
   - Never commit `.env` files to version control
   - Use environment variables in containerized deployments

3. **Monitoring:**
   - Monitor PostgreSQL logs for unauthorized access attempts
   - Set up alerts for connection failures
   - Monitor disk space and performance

4. **Backup:**
   - Set up automated database backups
   - Test backup restoration procedures
   - Store backups securely off-site

## Testing Your Current Setup

To verify everything is working with the updated configuration:

```bash
# Test as dx_scraper user
PGPASSWORD=dxdevtest psql -h localhost -U dx_scraper -d dxcluster -c "SELECT current_user, session_user;"

# Test permissions
PGPASSWORD=dxdevtest psql -h localhost -U dx_scraper -d dxcluster -c "INSERT INTO raw_spots (timestamp, raw_text) VALUES (NOW(), 'TEST') RETURNING id;"

# Test web user (read-only)
PGPASSWORD=dxdevtest psql -h localhost -U dx_web_user -d dxcluster -c "SELECT COUNT(*) FROM dx_spots;"
```

## Migration Script for Production

If you need to migrate from your current development setup to production with new passwords, you can use the `setup_production_db.sh` script which will:

1. Prompt for new secure passwords
2. Update the database roles with new credentials
3. Update your `.env` file automatically
4. Test the connection to ensure everything works

This ensures a smooth transition from development to production with proper security.