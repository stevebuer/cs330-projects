# DX Cluster Scraper - Complete Deployment Package v2.0.0

## Project Overview

This is the complete deployment package for the DX Cluster Scraper service with Prometheus metrics support, part of the CS 330 Homework 5 (Final Project).

The scraper:
- Monitors DX cluster feeds in real-time via socket connections
- Stores DX spots and WWV announcements in PostgreSQL
- Exports Prometheus metrics for monitoring and alerting
- Runs as a systemd service with automatic restart

## What Was Done

✓ Moved complete debian package build system from homework2 to homework5  
✓ Updated package for Prometheus metrics support (v2.0.0)  
✓ Created automated build scripts  
✓ Comprehensive documentation  
✓ Deployment guides and troubleshooting  

## Directory Structure

```
homework5/
├── dx_cluster_live_pg.py           # Main scraper script with Prometheus metrics
├── dx-scraper.service              # Local systemd service file
├── requirements.txt                # Python dependencies (includes prometheus-client)
├── PROMETHEUS_METRICS.md           # Metrics reference
├── SCRAPER_DEPLOYMENT_GUIDE.md     # Full deployment walkthrough
├── PACKAGE_MIGRATION_SUMMARY.md    # Migration details
├── docker-compose.yml
├── Dockerfile.api
└── packages/
    ├── Makefile                    # Build automation
    ├── build-scraper.sh            # Build script
    ├── README.md                   # Package documentation
    └── dxcluster-scraper/          # Debian package source
        ├── debian/
        │   ├── control             # Package metadata + dependencies
        │   ├── changelog           # Version history
        │   ├── rules               # Build rules
        │   └── ...
        ├── usr/bin/
        │   ├── dx_cluster_live_pg.py        # Main script
        │   ├── manage-scraper.sh
        │   └── load_dx_spots_pg.py
        ├── usr/share/
        │   └── dxcluster-scraper/
        │       └── requirements-pg.txt      # Python dependencies
        └── etc/
            ├── systemd/system/
            │   └── dx-scraper.service      # Production systemd service
            └── dxcluster/
                └── dxcluster.env.template  # Configuration template
```

## Quick Start

### 1. Build the Package

```bash
cd homework5/packages

# First time: install build dependencies
make install-deps

# Build the package
./build-scraper.sh
```

Output: `dxcluster-scraper_2.0.0-1_all.deb`

### 2. Install the Package

```bash
sudo dpkg -i dxcluster-scraper_2.0.0-1_all.deb
sudo apt-get install -f  # Install dependencies
```

### 3. Configure

```bash
sudo nano /etc/dxcluster/dxcluster.env
```

Set your database credentials, callsign, and Prometheus settings.

### 4. Run the Service

```bash
sudo systemctl enable dx-scraper
sudo systemctl start dx-scraper
sudo systemctl status dx-scraper
```

### 5. Monitor

```bash
# View metrics
curl http://localhost:8000/metrics

# View logs
sudo journalctl -u dx-scraper -f
```

## Key Files

### Build System
- **Makefile** - Build automation (`make build`, `make clean`, etc.)
- **build-scraper.sh** - Automated build with error checking

### Scraper Script
- **dx_cluster_live_pg.py** - Main monitoring script with:
  - Socket-based DX cluster connection
  - PostgreSQL data storage
  - Prometheus metrics export
  - Real-time parsing and filtering

### Package Configuration
- **debian/control** - Dependencies and metadata
- **debian/changelog** - Version 2.0.0 with Prometheus support
- **requirements-pg.txt** - Python dependencies including `prometheus-client`

### Systemd Service
- **dx-scraper.service** - Service configuration
  - Auto-restart on failure
  - Journal logging
  - Prometheus environment variables

### Documentation
- **SCRAPER_DEPLOYMENT_GUIDE.md** - Complete deployment walkthrough
- **PROMETHEUS_METRICS.md** - Available metrics reference
- **packages/README.md** - Package details and troubleshooting

## Prometheus Metrics

The scraper exports metrics on `http://localhost:8000/metrics`

### Key Metrics
```
# Connection Status
dx_scraper_cluster_connected         (1=connected, 0=disconnected)

# Ingestion Rate
rate(dx_scraper_spots_stored_total[5m])

# Uptime
dx_scraper_uptime_seconds / 3600     (in hours)

# Errors
dx_scraper_db_errors_total
dx_scraper_connection_errors_total

# Details by Band
dx_scraper_spots_stored_total{band="20m"}
```

## Configuration

Edit `/etc/dxcluster/dxcluster.env`:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dx_analysis
DB_USER=dx_scraper
DB_PASSWORD=your_password

# Your callsign
DEFAULT_CALLSIGN=N7MKO

# DX Cluster server
DEFAULT_HOST=dx.k3lr.com
DEFAULT_PORT=23

# Prometheus metrics
METRICS_ENABLED=true
METRICS_PORT=8000

# Frequency filtering
SKIP_FT8_FREQUENCIES=true
```

## Monitoring Setup

### Prometheus Configuration

Add to `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'dx-scraper'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    scrape_timeout: 10s
```

### Grafana Dashboards

Key queries for dashboards:

```promql
# Ingestion Rate
rate(dx_scraper_spots_stored_total[5m])

# Spots by Band
dx_scraper_spots_stored_total{}

# Connection Status
dx_scraper_cluster_connected

# Error Rate
rate(dx_scraper_db_errors_total[5m]) + rate(dx_scraper_connection_errors_total[5m])

# Database Latency (95th percentile)
histogram_quantile(0.95, dx_scraper_db_insert_seconds_bucket)
```

## Service Management

```bash
# Start/stop/restart
sudo systemctl start dx-scraper
sudo systemctl stop dx-scraper
sudo systemctl restart dx-scraper

# Enable auto-start
sudo systemctl enable dx-scraper
sudo systemctl disable dx-scraper

# Check status
sudo systemctl status dx-scraper
systemctl is-active dx-scraper

# View logs
sudo journalctl -u dx-scraper -f
sudo journalctl -u dx-scraper -n 100

# Resource usage
systemctl show dx-scraper --property=CPUUsageNSec,MemoryCurrent
```

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u dx-scraper -n 50

# Test database connection
psql -h localhost -U dx_scraper -d dx_analysis

# Run manually with debug
sudo -u dxcluster /usr/bin/dx_cluster_live_pg.py -d
```

### No metrics

```bash
# Check if metrics port is listening
sudo ss -tlnp | grep 8000

# Test endpoint
curl http://localhost:8000/metrics

# Check configuration
grep METRICS /etc/dxcluster/dxcluster.env
```

### Database errors

```bash
# Verify permissions
sudo -u postgres psql -d dx_analysis -c "\du"

# Check database
sudo -u postgres psql -d dx_analysis -c "SELECT COUNT(*) FROM dx_spots"
```

## Documentation Map

1. **SCRAPER_DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment
2. **PROMETHEUS_METRICS.md** - Available metrics and PromQL examples
3. **packages/README.md** - Package details, build, installation
4. **PACKAGE_MIGRATION_SUMMARY.md** - What was moved and changed
5. **This file** - Overview and quick reference

## Package Contents

**Version:** 2.0.0-1  
**Built:** November 22, 2024  
**Source:** homework5/packages/dxcluster-scraper  
**Install Path:** /usr/bin/, /etc/systemd/system/, /etc/dxcluster/  

### Installed Files
- `/usr/bin/dx_cluster_live_pg.py` - Main scraper
- `/usr/bin/manage-scraper.sh` - Service management
- `/usr/bin/load_dx_spots_pg.py` - Data loader
- `/etc/systemd/system/dx-scraper.service` - Service definition
- `/etc/dxcluster/dxcluster.env.template` - Configuration template
- `/usr/share/dxcluster-scraper/requirements-pg.txt` - Dependencies

## Dependencies

### System
- Python 3.8+
- PostgreSQL 12+
- Systemd
- Standard tools (curl, ssh, etc.)

### Python
- psycopg2-binary>=2.9.9
- python-dotenv>=1.0.0
- prometheus-client>=0.16.0

## Features

✓ Real-time DX cluster monitoring  
✓ PostgreSQL integration  
✓ Prometheus metrics (port 8000)  
✓ Systemd service management  
✓ Auto-restart on failure  
✓ Socket-based (no deprecated telnetlib)  
✓ Grid square extraction  
✓ WWV announcements  
✓ Frequency filtering  
✓ Comprehensive logging  
✓ Production-ready configuration  

## Build Targets

```bash
cd homework5/packages

make help          # Show help
make info          # Show package info
make install-deps  # Install build dependencies
make build         # Build the package
make clean         # Clean build artifacts
./build-scraper.sh # Alternative build script
```

## Performance Characteristics

**Typical Resource Usage:**
- CPU: 1-5% average
- Memory: 50-100 MB
- Network: 5-50 KB/sec from cluster
- Database: 1-2 concurrent connections

**Data Volume:**
- ~5,000-20,000 spots/day (varies by propagation)
- Database growth: ~50-200 MB/month

## Security

- Runs as unprivileged `dxcluster` system user
- Config file readable only by service user
- Database password in config file (protect /etc/dxcluster/dxcluster.env)
- Consider firewall rules for metrics endpoint
- Use strong database passwords

## Support Resources

1. **Deployment:** See `SCRAPER_DEPLOYMENT_GUIDE.md`
2. **Metrics:** See `PROMETHEUS_METRICS.md`
3. **Package:** See `packages/README.md`
4. **Logs:** `sudo journalctl -u dx-scraper -f`
5. **Metrics:** `curl http://localhost:8000/metrics`

## Next Steps

1. ✓ Review this document
2. → Build the package: `cd homework5/packages && ./build-scraper.sh`
3. → Follow `SCRAPER_DEPLOYMENT_GUIDE.md` for deployment
4. → Configure Prometheus/Grafana for monitoring
5. → Set up alert rules
6. → Monitor in production

## Version History

**2.0.0** (Nov 22, 2024)
- Prometheus metrics support
- Moved to homework5 final project
- Socket-based connections
- Python 3.11+ compatible

**1.1.0** (Oct 17, 2024)
- Socket-based (no telnetlib)
- Improved error handling

**1.0.0** (Oct 16, 2024)
- Initial release

---

**Project:** CS 330 Homework 5 - Databases (Final Project)  
**Package:** dxcluster-scraper v2.0.0-1  
**Author:** Steve Buer  
**Repository:** https://github.com/stevebuer/cs330-projects  
**Build Date:** November 22, 2024
