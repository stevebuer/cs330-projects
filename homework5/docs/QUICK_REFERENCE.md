# Quick Reference Card - DX Cluster Scraper v2.0.0

## Build & Deploy (30 seconds)

```bash
# Build
cd homework5/packages && ./build-scraper.sh

# Install
sudo dpkg -i dxcluster-scraper_2.0.0-1_all.deb && sudo apt-get install -f

# Configure
sudo nano /etc/dxcluster/dxcluster.env

# Start
sudo systemctl enable dx-scraper && sudo systemctl start dx-scraper

# Monitor
curl http://localhost:8000/metrics
```

## Essential Commands

### Service Management
```bash
sudo systemctl start dx-scraper       # Start service
sudo systemctl stop dx-scraper        # Stop service
sudo systemctl restart dx-scraper     # Restart service
sudo systemctl status dx-scraper      # Show status
sudo systemctl enable dx-scraper      # Enable auto-start
```

### Monitoring
```bash
sudo journalctl -u dx-scraper -f              # Real-time logs
curl http://localhost:8000/metrics            # All metrics
curl http://localhost:8000/metrics | grep dx_ # Filtered metrics
sudo systemctl show dx-scraper --property=*   # Service properties
```

### Database
```bash
psql -d dx_analysis -c "SELECT COUNT(*) FROM dx_spots"
psql -d dx_analysis -c "SELECT * FROM dx_spots ORDER BY timestamp DESC LIMIT 5"
psql -d dx_analysis -c "SELECT band, COUNT(*) FROM dx_spots GROUP BY band"
```

## Configuration

Edit: `/etc/dxcluster/dxcluster.env`

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dx_analysis
DB_USER=dx_scraper
DB_PASSWORD=password

# Scraper
DEFAULT_CALLSIGN=N7MKO
DEFAULT_HOST=dx.k3lr.com
DEFAULT_PORT=23

# Metrics
METRICS_ENABLED=true
METRICS_PORT=8000

# Filtering
SKIP_FT8_FREQUENCIES=true
```

## Key Metrics

```bash
# Connection status (1=connected, 0=disconnected)
curl -s http://localhost:8000/metrics | grep dx_scraper_cluster_connected

# Spots being stored (total since start)
curl -s http://localhost:8000/metrics | grep dx_scraper_spots_stored_total

# Error count
curl -s http://localhost:8000/metrics | grep dx_scraper_db_errors_total

# Service uptime (in seconds)
curl -s http://localhost:8000/metrics | grep dx_scraper_uptime_seconds
```

## Prometheus Queries

```promql
# Ingestion rate
rate(dx_scraper_spots_stored_total[5m])

# Connection status
dx_scraper_cluster_connected

# Error rate
rate(dx_scraper_db_errors_total[5m])

# Uptime in hours
dx_scraper_uptime_seconds / 3600

# Spots by band
dx_scraper_spots_stored_total{}
```

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u dx-scraper -n 20      # Check logs
sudo -u dxcluster /usr/bin/dx_cluster_live_pg.py -d  # Run manually
```

### No metrics
```bash
sudo ss -tlnp | grep 8000                # Check if listening
grep METRICS_ENABLED /etc/dxcluster/dxcluster.env
curl -v http://localhost:8000/metrics    # Test endpoint
```

### Database errors
```bash
psql -d dx_analysis -c "SELECT 1"        # Test connection
sudo -u postgres psql -d dx_analysis -c "\du"  # Check permissions
```

## File Locations

```
Config:         /etc/dxcluster/dxcluster.env
Service:        /etc/systemd/system/dx-scraper.service
Script:         /usr/bin/dx_cluster_live_pg.py
Logs:           journalctl -u dx-scraper
Metrics:        http://localhost:8000/metrics
```

## Build Targets

```bash
make help          # Show help
make info          # Show package info
make install-deps  # Install dependencies
make build         # Build package
make clean         # Clean artifacts
./build-scraper.sh # Alternative build
```

## Documentation Quick Links

- **Overview:** DEPLOYMENT_PACKAGE_OVERVIEW.md
- **Deployment:** SCRAPER_DEPLOYMENT_GUIDE.md
- **Verification:** DEPLOYMENT_CHECKLIST.md
- **Metrics:** PROMETHEUS_METRICS.md
- **Migration:** PACKAGE_MIGRATION_SUMMARY.md
- **Index:** DOCUMENTATION_INDEX.md

## Performance Baselines

- CPU: 1-5% average
- Memory: 50-100 MB
- Spots/Day: 5,000-20,000
- DB Growth: 50-200 MB/month
- DB Connections: 1-2 concurrent

## Version Info

- **Package:** dxcluster-scraper
- **Version:** 2.0.0-1
- **Date:** November 22, 2024
- **Project:** CS 330 Homework 5

## Emergency Commands

```bash
# Full restart
sudo systemctl restart dx-scraper

# Check everything
systemctl is-active dx-scraper && curl -s http://localhost:8000/metrics | wc -l

# Rebuild from scratch
cd homework5/packages && make clean && ./build-scraper.sh

# Full deployment
sudo systemctl stop dx-scraper && sudo dpkg -r dxcluster-scraper && \
cd homework5/packages && ./build-scraper.sh && \
sudo dpkg -i ../dxcluster-scraper_2.0.0-1_all.deb && \
sudo apt-get install -f && \
sudo systemctl start dx-scraper
```

---

**Project:** CS 330 Homework 5 - Databases  
**Package:** dxcluster-scraper v2.0.0-1  
**Status:** Production Ready  
**Last Updated:** November 22, 2024
