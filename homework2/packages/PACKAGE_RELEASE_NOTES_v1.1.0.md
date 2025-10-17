# DX Cluster Scraper Package v1.1.0 Release Notes

## Overview
This release replaces the deprecated `telnetlib` module with a modern socket-based implementation, ensuring compatibility with Python 3.11+ environments where `telnetlib` is no longer available.

## Package Details
- **Package Name**: `dxcluster-scraper`
- **Version**: `1.1.0-1`
- **Architecture**: `all`
- **Build Date**: October 17, 2024

## Key Changes

### ✅ BREAKING CHANGES
- **Replaced deprecated telnetlib with socket module**: The main script `dx_cluster_live_pg.py` now uses Python's built-in `socket` module instead of the deprecated `telnetlib`
- **Removed dependency on python3-telnetlib3**: No longer needed since we're using the standard socket library

### ✅ IMPROVEMENTS
- **Better connection reliability**: More robust error handling and connection management
- **Improved timeout handling**: Better management of socket timeouts and reconnection logic
- **Production ready**: Compatible with modern Python environments where telnetlib is not available
- **Same functionality**: All existing features preserved, just with a more reliable underlying connection

## Dependencies
```
python3
python3-psycopg2
python3-dotenv
systemd
dxcluster-database (>= 1.0.0)
```

## Installation

### Fresh Installation
```bash
sudo dpkg -i dxcluster-database_1.0.0-1_all.deb
sudo dpkg -i dxcluster-scraper_1.1.0-1_all.deb
sudo apt-get install -f  # Install any missing dependencies
```

### Upgrade from v1.0.0
```bash
sudo dpkg -i dxcluster-scraper_1.1.0-1_all.deb
sudo systemctl restart dx-scraper  # Restart the service with new code
```

## Files Included
- `/usr/bin/dx_cluster_live_pg.py` - Updated main DX cluster monitoring script
- `/usr/bin/load_dx_spots_pg.py` - Static data loading script
- `/usr/bin/manage-scraper.sh` - Service management script
- Systemd service files and configuration

## Testing Verification
The new socket-based implementation has been tested and verified to:
- ✅ Successfully connect to DX cluster servers (tested with dx.k3lr.com:23)
- ✅ Parse and store DX spots in PostgreSQL database
- ✅ Handle connection timeouts and reconnection properly
- ✅ Maintain all existing functionality without telnetlib dependency

## Migration Notes
- **No configuration changes required**: The script uses the same environment variables and database setup
- **No database schema changes**: All existing data remains compatible
- **Service configuration unchanged**: The systemd service continues to work as before

## Support
For issues or questions about this release, check the chat transcripts in the `chat-transcripts/` directory or refer to the project documentation.

---
**Built on**: October 17, 2024  
**Maintainer**: Steve Buer <steve@example.com>  
**Project**: CS330 Projects - DX Cluster Monitoring System