# DX Scraper Service Management

The DX scraper functionality has been separated from the web application and is now managed through systemctl. This provides better service management, automatic restarts, and proper logging.

## Files Created

1. **`dx-scraper.service`** - Systemd service file
2. **`manage-scraper.sh`** - Management script for easy control

## Installation

To install the DX scraper as a system service:

```bash
cd /home/steve/GITHUB/cs330-projects/homework2
./manage-scraper.sh install
```

## Service Management Commands

### Basic Operations
```bash
# Start the scraper
./manage-scraper.sh start

# Stop the scraper
./manage-scraper.sh stop

# Restart the scraper
./manage-scraper.sh restart

# Check status
./manage-scraper.sh status
```

### Boot Management
```bash
# Enable auto-start on boot
./manage-scraper.sh enable

# Disable auto-start on boot
./manage-scraper.sh disable
```

### Monitoring
```bash
# View recent logs
./manage-scraper.sh logs

# Follow logs in real-time
sudo journalctl -u dx-scraper -f
```

### Uninstalling
```bash
# Remove the service
./manage-scraper.sh uninstall
```

## Service Configuration

The service is configured to:
- Run as user `steve`
- Automatically restart on failure
- Wait for PostgreSQL to be available
- Log to systemd journal
- Use the project's virtual environment
- Load environment variables from `.env` file

## Web Application Changes

The web application has been simplified to focus on data visualization and monitoring:

### Removed Features
- Scraper start/stop buttons
- Scraper status display
- Log viewer
- Scraper error messages

### Enhanced Features
- **4-column statistics** - Total spots today, active stations, latest update, total records
- **24-hour statistics** - Detailed breakdown of last 24 hours
- **7-day statistics** - Weekly overview
- **Improved layout** - More space for data visualization
- **Better error handling** - Graceful fallback to demo data

## Benefits of This Separation

1. **Better Service Management** - Use standard Linux service management tools
2. **Automatic Recovery** - Service restarts automatically on failure
3. **System Integration** - Proper boot integration and dependency management
4. **Better Logging** - Centralized logging through systemd journal
5. **Security** - Service runs with proper user permissions
6. **Cleaner Web Interface** - Web app focuses on visualization, not control

## Monitoring the Service

### Check if service is running
```bash
systemctl is-active dx-scraper
```

### View service status
```bash
systemctl status dx-scraper
```

### Monitor resource usage
```bash
systemctl show dx-scraper --property=CPUUsageNSec,MemoryCurrent
```

### Real-time log monitoring
```bash
journalctl -u dx-scraper -f --no-pager
```

## Troubleshooting

If the service fails to start:

1. Check the service status: `./manage-scraper.sh status`
2. View the logs: `./manage-scraper.sh logs`
3. Verify the environment file exists: `ls -la .env`
4. Check Python virtual environment: `ls -la /home/steve/GITHUB/cs330-projects/.venv/bin/python`
5. Verify the scraper script exists: `ls -la load_dx_spots_pg.py`

## Database Configuration

Make sure your `.env` file contains the correct database connection parameters:
```
PGHOST=localhost
PGDATABASE=your_database_name
PGUSER=your_username
PGPASSWORD=your_password
```

The service will automatically load these environment variables and use them for database connections.