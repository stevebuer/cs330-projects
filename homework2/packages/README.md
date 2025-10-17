# DX Cluster Debian Packages

This directory contains Debian packages for deploying the DX Cluster monitoring system in production environments.

## Packages

### 1. dxcluster-database
**Database schema and setup components**

**Contents:**
- PostgreSQL database schema creation scripts
- Database user role and permission setup
- Production configuration templates
- Interactive setup utilities

**Files installed:**
- `/usr/bin/init_dx_database_pg.py` - Database schema initialization
- `/usr/share/dxcluster-database/setup_db_roles.sql` - User roles and permissions
- `/usr/share/dxcluster-database/setup_production_db.sh` - Interactive setup script
- `/usr/share/dxcluster-database/.env.production.template` - Configuration template

### 2. dxcluster-scraper  
**DX cluster monitoring service**

**Contents:**
- Telnet-based DX cluster monitoring scripts
- Systemd service configuration
- Service management utilities
- Production-ready configuration

**Files installed:**
- `/usr/bin/dx_cluster_live_pg.py` - Live DX cluster monitoring
- `/usr/bin/load_dx_spots_pg.py` - Data loading and processing
- `/usr/bin/manage-scraper.sh` - Service management script
- `/etc/systemd/system/dx-scraper.service` - Systemd service definition
- `/etc/dxcluster/dxcluster.env.template` - Configuration template

## Installation

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install postgresql python3 python3-psycopg2 python3-dotenv
```

### Install Database Package
```bash
sudo dpkg -i dxcluster-database_1.0.0-1_all.deb
sudo apt-get install -f  # Fix any missing dependencies
```

### Install Scraper Package
```bash
sudo dpkg -i dxcluster-scraper_1.0.0-1_all.deb
sudo apt-get install -f  # Fix any missing dependencies
```

## Configuration

### Database Setup
1. Create the PostgreSQL database:
   ```bash
   sudo -u postgres createdb dxcluster
   ```

2. Initialize the schema:
   ```bash
   sudo -u postgres init_dx_database_pg.py
   ```

3. Set up user roles (interactive):
   ```bash
   /usr/share/dxcluster-database/setup_production_db.sh
   ```

### Scraper Service Setup
1. Edit the configuration file:
   ```bash
   sudo nano /etc/dxcluster/dxcluster.env
   ```
   
   Configure:
   - Database connection parameters
   - Your callsign
   - DX cluster server details

2. Start the service:
   ```bash
   sudo systemctl enable dx-scraper
   sudo systemctl start dx-scraper
   ```

3. Check service status:
   ```bash
   sudo systemctl status dx-scraper
   ```

## Building from Source

### Install Build Dependencies
```bash
sudo apt-get install debhelper dpkg-dev build-essential
```

### Build Packages
```bash
# Build both packages
make all

# Build individual packages
make build-database
make build-scraper

# Or use the build script
./build-packages.sh
```

### Available Make Targets
- `all` - Build both packages
- `build-database` - Build database package only
- `build-scraper` - Build scraper package only
- `install` - Install both packages
- `install-database` - Install database package only
- `install-scraper` - Install scraper package only
- `clean` - Clean build artifacts
- `install-deps` - Install build dependencies
- `info` - Show help information

## Package Details

### Dependencies
**dxcluster-database:**
- postgresql
- python3
- python3-psycopg2
- python3-dotenv

**dxcluster-scraper:**
- python3
- python3-psycopg2
- python3-dotenv
- python3-telnetlib3
- systemd
- dxcluster-database (>= 1.0.0)

### Service Management
The scraper service can be managed using standard systemd commands:

```bash
# Service control
sudo systemctl start dx-scraper
sudo systemctl stop dx-scraper
sudo systemctl restart dx-scraper
sudo systemctl status dx-scraper

# Enable/disable auto-start
sudo systemctl enable dx-scraper
sudo systemctl disable dx-scraper

# View logs
sudo journalctl -u dx-scraper -f
```

Or use the included management script:
```bash
manage-scraper.sh start
manage-scraper.sh stop  
manage-scraper.sh status
manage-scraper.sh logs
```

## Security Considerations

1. **Database Passwords**: Change default passwords during setup
2. **User Permissions**: The scraper runs as the `dxcluster` system user
3. **File Permissions**: Configuration files are readable only by appropriate users
4. **Network Security**: Consider firewall rules for database connections

## Troubleshooting

### Database Connection Issues
```bash
# Test database connection
sudo -u dxcluster psql -h localhost -U dx_scraper -d dxcluster

# Check PostgreSQL service
sudo systemctl status postgresql
```

### Service Issues
```bash
# Check service logs
sudo journalctl -u dx-scraper -n 50

# Test scripts manually
sudo -u dxcluster /usr/bin/load_dx_spots_pg.py
```

### Package Issues
```bash
# Reinstall packages
sudo dpkg -r dxcluster-scraper dxcluster-database
sudo dpkg -i *.deb
sudo apt-get install -f
```

## Uninstallation

```bash
# Remove packages (keep configuration)
sudo dpkg -r dxcluster-scraper dxcluster-database

# Completely remove with configuration
sudo dpkg --purge dxcluster-scraper dxcluster-database
```

## Support

For issues and questions:
- Check the logs: `sudo journalctl -u dx-scraper`
- Verify configuration: `/etc/dxcluster/dxcluster.env`
- Test database connectivity manually
- Review the chat transcripts in the source repository