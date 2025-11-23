# DX Cluster Scraper Debian Package

This directory contains the Debian package build system for the DX Cluster Scraper service with Prometheus metrics support.

## Package Contents

The `dxcluster-scraper` package provides:

- **DX Cluster Monitoring**: Real-time socket-based monitoring of DX cluster feeds
- **PostgreSQL Integration**: Automatic storage of DX spots in a PostgreSQL database
- **Prometheus Metrics**: Export of monitoring metrics in Prometheus format on port 8000
- **Systemd Service**: Automatic service management and restart capability

## Features

- ✓ Live DX spot parsing and filtering
- ✓ WWV propagation announcements tracking
- ✓ Prometheus metrics export (port 8000)
- ✓ Systemd service integration
- ✓ Grid square extraction and storage
- ✓ Automatic error recovery
- ✓ Configurable frequency filtering (FT8, etc.)

## Installation

### Prerequisites

- Debian/Ubuntu system
- PostgreSQL server (local or remote)
- Python 3.8+
- Systemd

### Quick Install

```bash
# Build the package
cd homework5/packages
./build-scraper.sh

# Install the package
sudo dpkg -i ../dxcluster-scraper_2.0.0-1_all.deb

# Install any missing dependencies
sudo apt-get install -f
```

### Build from Source

```bash
cd homework5/packages

# Install build dependencies
make install-deps

# Build the package
make build

# Or build directly
./build-scraper.sh
```

## Configuration

### Environment Setup

Edit `/etc/dxcluster/dxcluster.env` with your configuration:

```bash
sudo nano /etc/dxcluster/dxcluster.env
```

Required variables:

```bash
# Database connection
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

# Prometheus metrics (optional)
METRICS_ENABLED=true
METRICS_PORT=8000

# Frequency filtering
SKIP_FT8_FREQUENCIES=true
```

### Systemd Service Management

```bash
# Enable auto-start on boot
sudo systemctl enable dx-scraper

# Start the service
sudo systemctl start dx-scraper

# Check status
sudo systemctl status dx-scraper

# View logs
sudo journalctl -u dx-scraper -f

# Stop the service
sudo systemctl stop dx-scraper

# Restart the service
sudo systemctl restart dx-scraper
```

## Prometheus Metrics

### Available Metrics

The scraper exports metrics on `http://localhost:8000/metrics`:

#### Counters
- `dx_scraper_spots_total` - Total DX spots received (by band, mode)
- `dx_scraper_spots_stored_total` - Spots successfully stored (by band, mode)
- `dx_scraper_spots_filtered_total` - Spots filtered out (by reason)
- `dx_scraper_wwv_total` - WWV announcements received
- `dx_scraper_wwv_stored_total` - WWV announcements stored
- `dx_scraper_db_errors_total` - Database errors
- `dx_scraper_connection_errors_total` - Connection errors

#### Gauges
- `dx_scraper_lines_received_total` - Total lines received
- `dx_scraper_spots_received` - Spots since start
- `dx_scraper_uptime_seconds` - Service uptime
- `dx_scraper_last_spot_timestamp` - Last spot timestamp
- `dx_scraper_cluster_connected` - Connection status (1=connected, 0=disconnected)

#### Histograms
- `dx_scraper_db_insert_seconds` - Database insert latency

### Query Metrics

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Get specific metric
curl http://localhost:8000/metrics | grep dx_scraper_spots_stored_total
```

### Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'dx-scraper'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    scrape_timeout: 10s
```

## Monitoring

### Service Monitoring

```bash
# Check if service is running
systemctl is-active dx-scraper

# Check service health
curl http://localhost:8000/metrics | grep dx_scraper_cluster_connected

# Monitor real-time
sudo journalctl -u dx-scraper -f --no-pager

# Check CPU/Memory usage
systemctl show dx-scraper --property=CPUUsageNSec,MemoryCurrent
```

### Grafana Integration

Key metrics for Grafana dashboards:

1. **Ingestion Rate**: `rate(dx_scraper_spots_stored_total[5m])`
2. **Spots by Band**: `dx_scraper_spots_stored_total{}`
3. **Connection Status**: `dx_scraper_cluster_connected`
4. **Uptime**: `dx_scraper_uptime_seconds / 3600` (in hours)
5. **DB Latency (95th percentile)**: `histogram_quantile(0.95, dx_scraper_db_insert_seconds_bucket)`
6. **Error Rate**: `rate(dx_scraper_db_errors_total[5m]) + rate(dx_scraper_connection_errors_total[5m])`

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u dx-scraper -n 50

# Test connection
python3 -c "import psycopg2; psycopg2.connect(host='localhost', database='dx_analysis', user='dx_scraper')"

# Check database exists
sudo -u postgres psql -l | grep dx_analysis
```

### No metrics available

```bash
# Check if metrics port is accessible
curl http://localhost:8000/metrics

# Check if metrics are enabled
grep METRICS_ENABLED /etc/dxcluster/dxcluster.env

# Check firewall
sudo ufw status | grep 8000
```

### High database errors

```bash
# Check database permissions
sudo -u postgres psql -c "SELECT * FROM information_schema.role_table_grants WHERE grantee='dx_scraper';"

# Verify user exists
sudo -u postgres psql -c "\du dx_scraper"
```

## Package Files

- `dxcluster-scraper/debian/` - Debian package metadata
  - `control` - Package dependencies and description
  - `rules` - Build rules
  - `changelog` - Version history
  - `postinst` - Post-installation script
  - `postrm` - Post-removal script

- `dxcluster-scraper/usr/bin/` - Executable scripts
  - `dx_cluster_live_pg.py` - Main scraper service
  - `manage-scraper.sh` - Service management script

- `dxcluster-scraper/usr/share/` - Data files
  - `dxcluster-scraper/requirements-pg.txt` - Python dependencies

- `dxcluster-scraper/etc/` - Configuration files
  - `systemd/system/dx-scraper.service` - Systemd unit file
  - `dxcluster/dxcluster.env.template` - Configuration template

## Build Targets

```bash
make help          # Show help
make info          # Show package info
make install-deps  # Install build dependencies
make build         # Build package
make clean         # Clean build artifacts
```

## Version History

### 2.0.0
- Added Prometheus metrics support
- Updated to socket-based (no deprecated telnetlib)
- Moved to homework5 for final project
- Enhanced error handling and logging

### 1.0.0
- Initial package release
- PostgreSQL integration
- Systemd service

## Support

For issues:
1. Check logs: `sudo journalctl -u dx-scraper`
2. Verify configuration: `/etc/dxcluster/dxcluster.env`
3. Test metrics endpoint: `curl http://localhost:8000/metrics`
4. Review repository: https://github.com/stevebuer/cs330-projects

## License

Part of CS 330 Homework - Databases Project
