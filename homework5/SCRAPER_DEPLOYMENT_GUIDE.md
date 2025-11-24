# DX Cluster Scraper Deployment Guide

Complete guide for deploying the DX Cluster Scraper package v2.0.0 with Prometheus metrics support.

## Overview

This guide covers deploying the `dxcluster-scraper` Debian package, which:

- Monitors DX cluster feeds in real-time
- Stores DX spots in PostgreSQL
- Exports Prometheus metrics for monitoring
- Integrates with systemd for service management

## Prerequisites

- Ubuntu/Debian system (18.04+)
- PostgreSQL 12+ (local or remote)
- Python 3.8+
- Sudo access
- Network connectivity to DX cluster servers
- (Optional) Prometheus and Grafana for monitoring

## Step 1: Build the Package

### On your build machine:

```bash
cd ~/cs330-projects/homework5/packages

# Install build dependencies if needed
make install-deps

# Build the package
./build-scraper.sh
```

This creates: `dxcluster-scraper_2.0.0-1_all.deb`

## Step 2: Prepare the Deployment System

### Install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip postgresql-client systemd
```

### Create dxcluster system user:

```bash
# Create user for running the service
sudo useradd -r -s /bin/false -d /var/lib/dxcluster dxcluster

# Create working directory
sudo mkdir -p /var/lib/dxcluster
sudo chown dxcluster:dxcluster /var/lib/dxcluster
```

## Step 3: Install the Package

```bash
# Copy package to deployment system (if different machine)
scp dxcluster-scraper_2.0.0-1_all.deb user@deployment-host:~

# Install the package
sudo dpkg -i dxcluster-scraper_2.0.0-1_all.deb

# Install missing dependencies
sudo apt-get install -f
```

## Step 4: Configure the Scraper

### Edit configuration file:

```bash
sudo nano /etc/dxcluster/dxcluster.env
```

### Required configuration:

```bash
# Database connection parameters
DB_HOST=localhost                    # or your database server IP
DB_PORT=5432
DB_NAME=dx_analysis
DB_USER=dx_scraper
DB_PASSWORD=your_secure_password     # CHANGE THIS!

# Your amateur radio callsign
DEFAULT_CALLSIGN=N7MKO              # CHANGE THIS!

# DX Cluster server to connect to
DEFAULT_HOST=dx.k3lr.com
DEFAULT_PORT=23

# Prometheus metrics configuration
METRICS_ENABLED=true
METRICS_PORT=8000

# Frequency filtering (skip FT8 digital mode frequencies)
SKIP_FT8_FREQUENCIES=true
```

### Set secure permissions:

```bash
sudo chmod 600 /etc/dxcluster/dxcluster.env
sudo chown dxcluster:dxcluster /etc/dxcluster/dxcluster.env
```

## Step 5: Verify Database

### Create database and user (if not already done):

```bash
# Connect as postgres user
sudo -u postgres psql

# In psql:
CREATE DATABASE dx_analysis;
CREATE USER dx_scraper WITH PASSWORD 'your_secure_password';
ALTER ROLE dx_scraper SET client_encoding TO 'utf8';
ALTER ROLE dx_scraper SET default_transaction_isolation TO 'read committed';
ALTER ROLE dx_scraper SET default_transaction_deferrable TO on;
ALTER ROLE dx_scraper SET timezone TO 'UTC';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dx_analysis TO dx_scraper;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dx_scraper;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dx_scraper;

-- Exit psql
\q
```

### Initialize database schema:

```bash
sudo -u dxcluster python3 /usr/bin/init_dx_database_pg.py
```

If running on a different machine, you may need to run initialization first.

## Step 6: Enable and Start the Service

```bash
# Enable auto-start on boot
sudo systemctl enable dx-scraper

# Start the service
sudo systemctl start dx-scraper

# Verify it's running
sudo systemctl status dx-scraper

# View live logs
sudo journalctl -u dx-scraper -f
```

## Step 7: Verify Prometheus Metrics

### Test metrics endpoint:

```bash
# Query all metrics
curl http://localhost:8000/metrics

# Check connection status
curl http://localhost:8000/metrics | grep dx_scraper_cluster_connected

# Check ingestion rate
curl http://localhost:8000/metrics | grep dx_scraper_spots_stored_total
```

## Step 8: Set Up Prometheus Monitoring (Optional)

### Edit Prometheus configuration:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

### Add scraper job:

```yaml
scrape_configs:
  - job_name: 'dx-scraper'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: '/metrics'
```

### Reload Prometheus:

```bash
sudo systemctl reload prometheus
```

## Step 9: Set Up Grafana Dashboard (Optional)

### Create dashboard queries:

**Ingestion Rate:**
```promql
rate(dx_scraper_spots_stored_total[5m])
```

**Connection Status:**
```promql
dx_scraper_cluster_connected
```

**Scraper Uptime (hours):**
```promql
dx_scraper_uptime_seconds / 3600
```

**Error Rate:**
```promql
rate(dx_scraper_db_errors_total[5m]) + rate(dx_scraper_connection_errors_total[5m])
```

**Spots by Band:**
```promql
dx_scraper_spots_stored_total{}
```

## Troubleshooting

### Service fails to start

```bash
# Check logs for errors
sudo journalctl -u dx-scraper -n 100

# Test database connection
sudo -u dxcluster psql -h localhost -U dx_scraper -d dx_analysis -c "SELECT 1"

# Verify configuration
sudo cat /etc/dxcluster/dxcluster.env

# Test script manually
sudo -u dxcluster /usr/bin/dx_cluster_live_pg.py -d
```

### Database connection errors

```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep dx_analysis

# Verify user has permissions
sudo -u postgres psql -c "\dp dx_analysis.*"

# Test connection with credentials
psql -h localhost -U dx_scraper -d dx_analysis
```

### No metrics available

```bash
# Check if metrics port is listening
sudo netstat -tlnp | grep 8000
# or
sudo ss -tlnp | grep 8000

# Check if metrics are enabled in config
grep METRICS_ENABLED /etc/dxcluster/dxcluster.env

# Firewall check
sudo ufw status | grep 8000
sudo iptables -L -n | grep 8000
```

### Service crashes frequently

```bash
# Enable debug output
sudo systemctl stop dx-scraper
sudo -u dxcluster /usr/bin/dx_cluster_live_pg.py -d

# Check resource usage
top -p $(pidof python3)

# Increase log level
sudo journalctl -u dx-scraper -f --lines 50
```

## Monitoring Commands

### Check service health:

```bash
# Status
systemctl is-active dx-scraper

# Resource usage
systemctl show dx-scraper --property=CPUUsageNSec,MemoryCurrent

# Restart count
systemctl show dx-scraper --property=NRestarts

# Uptime
systemctl show dx-scraper --property=ExecMainStartTimestamp
```

### Monitor in real-time:

```bash
# Live logs
sudo journalctl -u dx-scraper -f --no-pager

# Follow metrics
watch 'curl -s http://localhost:8000/metrics | grep -E "^dx_scraper"'
```

### Database monitoring:

```bash
# Check spot count
sudo -u postgres psql -d dx_analysis -c "SELECT COUNT(*) as total_spots FROM dx_spots"

# Latest spots
sudo -u postgres psql -d dx_analysis -c "SELECT * FROM dx_spots ORDER BY timestamp DESC LIMIT 5"

# Spots by band
sudo -u postgres psql -d dx_analysis -c "SELECT band, COUNT(*) FROM dx_spots GROUP BY band ORDER BY COUNT DESC"
```

## Maintenance

### View logs:

```bash
# Last 100 lines
sudo journalctl -u dx-scraper -n 100

# Last hour
sudo journalctl -u dx-scraper --since "1 hour ago"

# By priority
sudo journalctl -u dx-scraper -p err

# Real-time
sudo journalctl -u dx-scraper -f
```

### Restart service:

```bash
sudo systemctl restart dx-scraper
```

### Update configuration:

```bash
# Edit config
sudo nano /etc/dxcluster/dxcluster.env

# Restart to apply
sudo systemctl restart dx-scraper
```

### Stop service:

```bash
sudo systemctl stop dx-scraper
sudo systemctl disable dx-scraper  # Also disable auto-start
```

## Security Considerations

1. **Database Password**: Use strong passwords and update `dxcluster.env`
2. **File Permissions**: Config file should be readable only by dxcluster user
3. **Network**: Restrict Prometheus metrics endpoint if needed
4. **User Account**: Service runs as unprivileged `dxcluster` user
5. **Logs**: Be aware sensitive data may appear in logs

## Performance Tuning

### Connection pooling:

If connecting to remote database, consider:
- Network latency (adjust timeouts)
- Connection pool size
- Database indexes

### Metrics retention:

For Prometheus:
- Default retention: 15 days
- Adjust in `prometheus.yml`: `--storage.tsdb.retention.time=30d`

### CPU/Memory:

Typical usage:
- CPU: 1-5% average
- Memory: 50-100 MB
- Connections: 1-2 to database

## Uninstallation

```bash
# Stop service
sudo systemctl stop dx-scraper
sudo systemctl disable dx-scraper

# Remove package (keep config)
sudo dpkg -r dxcluster-scraper

# Remove package completely
sudo dpkg --purge dxcluster-scraper

# Optional: remove database
sudo -u postgres dropdb dx_analysis
sudo -u postgres dropuser dx_scraper
```

## Next Steps

1. Monitor metrics in Prometheus
2. Create Grafana dashboards
3. Set up alert rules
4. Integrate with existing monitoring
5. Document deployment in your infrastructure

## Support

For issues:
- Check logs: `sudo journalctl -u dx-scraper -f`
- Verify config: `/etc/dxcluster/dxcluster.env`
- Test endpoint: `curl http://localhost:8000/metrics`
- Review build guide in `/usr/share/dxcluster-scraper/`

## Version

- Package: dxcluster-scraper
- Version: 2.0.0-1
- Release Date: November 22, 2024
- Project: CS 330 Homework 5 (Final Project)
