# Deployment Checklist & Verification

## Package Migration - COMPLETE ✓

This checklist verifies the successful migration and setup of the dxcluster-scraper package to homework5 with Prometheus metrics support.

## Pre-Deployment Verification

### ✓ Package Structure
- [x] `homework5/packages/dxcluster-scraper/` directory exists
- [x] `debian/` metadata directory present
- [x] `usr/bin/` executables copied
- [x] `usr/share/` resources present
- [x] `etc/` configuration templates ready

### ✓ Build System
- [x] `homework5/packages/Makefile` created
- [x] `homework5/packages/build-scraper.sh` created and executable
- [x] Build scripts have proper error handling
- [x] Dependency checking in place

### ✓ Documentation
- [x] `DEPLOYMENT_PACKAGE_OVERVIEW.md` - Overview
- [x] `SCRAPER_DEPLOYMENT_GUIDE.md` - Step-by-step deployment
- [x] `PROMETHEUS_METRICS.md` - Metrics reference
- [x] `PACKAGE_MIGRATION_SUMMARY.md` - Migration details
- [x] `packages/README.md` - Package documentation
- [x] This checklist document

## Package Updates - COMPLETE ✓

### ✓ debian/control
- [x] Added `python3-prometheus-client` dependency
- [x] Updated description with metrics mention
- [x] Maintained all other dependencies

### ✓ debian/changelog
- [x] Version 2.0.0-1 entry added
- [x] Date set to November 22, 2024
- [x] Prometheus features documented
- [x] Relocation to homework5 noted

### ✓ requirements-pg.txt
- [x] Added `prometheus-client>=0.16.0`
- [x] Kept existing dependencies
- [x] Proper version pinning

### ✓ dx-scraper.service
- [x] Updated script name (load_dx_spots_pg.py → dx_cluster_live_pg.py)
- [x] Added `METRICS_ENABLED=true`
- [x] Added `METRICS_PORT=8000`
- [x] Maintained all other settings

### ✓ dx_cluster_live_pg.py
- [x] Latest version with Prometheus integration
- [x] Metrics counters implemented
- [x] Metrics gauges implemented
- [x] Metrics histograms implemented
- [x] HTTP metrics endpoint on port 8000
- [x] Environment variable configuration

## File Locations

### Verified Locations
- [x] `homework5/dx_cluster_live_pg.py` - Main script
- [x] `homework5/dx-scraper.service` - Local service file
- [x] `homework5/requirements.txt` - Dependencies
- [x] `homework5/packages/dxcluster-scraper/` - Package source

### Package Contents
- [x] `/usr/bin/dx_cluster_live_pg.py`
- [x] `/usr/bin/manage-scraper.sh`
- [x] `/usr/bin/load_dx_spots_pg.py`
- [x] `/etc/systemd/system/dx-scraper.service`
- [x] `/etc/dxcluster/dxcluster.env.template`
- [x] `/usr/share/dxcluster-scraper/requirements-pg.txt`

## Pre-Build Steps

Before building the package, verify:

- [ ] You have build-essential installed: `sudo apt-get install -y build-essential debhelper dpkg-dev`
- [ ] Python 3 is available: `python3 --version`
- [ ] PostgreSQL client is available: `psql --version`
- [ ] You're in the homework5 directory: `cd ~/cs330-projects/homework5`

## Build Verification

### Step 1: Install Dependencies

```bash
cd homework5/packages
make install-deps
```

Verify:
- [ ] debhelper installed
- [ ] dpkg-dev installed
- [ ] No errors in output

### Step 2: Build Package

```bash
./build-scraper.sh
```

Verify:
- [ ] Build successful message appears
- [ ] No errors during debuild
- [ ] Package file created: `dxcluster-scraper_2.0.0-1_all.deb`

### Step 3: Verify Package

```bash
cd /home/steve/GITHUB/cs330-projects/homework5
ls -lh dxcluster-scraper_2.0.0-1_all.deb
dpkg -I dxcluster-scraper_2.0.0-1_all.deb
```

Verify:
- [ ] Package file exists and is readable
- [ ] Package metadata shows version 2.0.0-1
- [ ] Depends list includes prometheus-client
- [ ] Architecture is "all"

## Pre-Installation Steps

Before installing, prepare the system:

### Step 1: System User

```bash
sudo useradd -r -s /bin/false -d /var/lib/dxcluster dxcluster 2>/dev/null || true
sudo mkdir -p /var/lib/dxcluster
sudo chown dxcluster:dxcluster /var/lib/dxcluster
```

Verify:
- [ ] User `dxcluster` exists: `id dxcluster`
- [ ] Directory `/var/lib/dxcluster` exists and has correct permissions

### Step 2: Database

```bash
# As postgres user, create database and user (if needed)
sudo -u postgres createdb dx_analysis
sudo -u postgres psql -c "CREATE USER dx_scraper WITH PASSWORD 'your_password'"
```

Verify:
- [ ] Database `dx_analysis` exists
- [ ] User `dx_scraper` exists
- [ ] Permissions properly set

## Installation Steps

### Step 1: Install Package

```bash
cd /home/steve/GITHUB/cs330-projects/homework5
sudo dpkg -i dxcluster-scraper_2.0.0-1_all.deb
```

Verify:
- [ ] No errors during installation
- [ ] Files installed to correct locations

### Step 2: Install Dependencies

```bash
sudo apt-get install -f
```

Verify:
- [ ] All dependencies installed
- [ ] No dependency conflicts

### Step 3: Verify Installation

```bash
ls -l /usr/bin/dx_cluster_live_pg.py
ls -l /etc/systemd/system/dx-scraper.service
ls -l /etc/dxcluster/dxcluster.env.template
```

Verify:
- [ ] All files present
- [ ] Correct permissions (executable where needed)

## Configuration Steps

### Step 1: Create Configuration

```bash
sudo cp /etc/dxcluster/dxcluster.env.template /etc/dxcluster/dxcluster.env
sudo nano /etc/dxcluster/dxcluster.env
```

Set:
- [ ] `DB_HOST` - Your database host
- [ ] `DB_PORT` - Usually 5432
- [ ] `DB_NAME` - dx_analysis
- [ ] `DB_USER` - dx_scraper
- [ ] `DB_PASSWORD` - Your database password
- [ ] `DEFAULT_CALLSIGN` - Your callsign
- [ ] `METRICS_ENABLED` - true
- [ ] `METRICS_PORT` - 8000

### Step 2: Set Permissions

```bash
sudo chmod 600 /etc/dxcluster/dxcluster.env
sudo chown dxcluster:dxcluster /etc/dxcluster/dxcluster.env
```

Verify:
- [ ] File is readable only by dxcluster user
- [ ] No world-readable access

### Step 3: Test Configuration

```bash
sudo -u dxcluster cat /etc/dxcluster/dxcluster.env
```

Verify:
- [ ] No permission denied errors
- [ ] Configuration values are correct

## Service Startup Steps

### Step 1: Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable dx-scraper
```

Verify:
- [ ] No errors from daemon-reload
- [ ] Service enabled for auto-start

### Step 2: Start Service

```bash
sudo systemctl start dx-scraper
```

Verify:
- [ ] No errors during start
- [ ] Service starts without issues

### Step 3: Verify Service

```bash
sudo systemctl status dx-scraper
systemctl is-active dx-scraper
```

Verify:
- [ ] Service is active (running)
- [ ] No error messages
- [ ] Status shows "active (running)"

## Runtime Verification

### Step 1: Check Logs

```bash
sudo journalctl -u dx-scraper -n 20
```

Verify:
- [ ] No error messages
- [ ] Connection messages present
- [ ] Database operations logged

### Step 2: Test Metrics

```bash
curl -s http://localhost:8000/metrics | head -20
curl -s http://localhost:8000/metrics | grep dx_scraper_cluster_connected
```

Verify:
- [ ] Metrics endpoint responds
- [ ] Prometheus format output
- [ ] Connection status metric present

### Step 3: Monitor Real-time

```bash
sudo journalctl -u dx-scraper -f
```

Verify:
- [ ] DX spots being received
- [ ] Database storage occurring
- [ ] No continuous errors
- [ ] Metrics being exported

## Database Verification

### Step 1: Check Data

```bash
sudo -u postgres psql -d dx_analysis -c "SELECT COUNT(*) as total_spots FROM dx_spots"
```

Verify:
- [ ] Spots being stored (count > 0)
- [ ] No database errors
- [ ] Proper user permissions

### Step 2: Latest Spots

```bash
sudo -u postgres psql -d dx_analysis -c "SELECT * FROM dx_spots ORDER BY timestamp DESC LIMIT 5"
```

Verify:
- [ ] Recent spots present
- [ ] Data looks correct
- [ ] Timestamps are recent

## Prometheus Integration (Optional)

### Step 1: Configure Prometheus

Edit `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'dx-scraper'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
```

### Step 2: Reload Prometheus

```bash
sudo systemctl reload prometheus
```

Verify:
- [ ] No errors during reload
- [ ] Targets showing in Prometheus UI

### Step 3: Query Metrics

In Prometheus UI, run:
```promql
rate(dx_scraper_spots_stored_total[5m])
dx_scraper_cluster_connected
```

Verify:
- [ ] Metrics appear in query results
- [ ] Values are non-zero (where applicable)

## Production Verification

### Daily Operations

- [ ] Service is running: `systemctl is-active dx-scraper`
- [ ] Spots being stored: `SELECT COUNT(*) FROM dx_spots WHERE timestamp > NOW() - INTERVAL '1 day'`
- [ ] No errors: `sudo journalctl -u dx-scraper --since "1 hour ago" | grep -i error`
- [ ] Metrics flowing: `curl -s http://localhost:8000/metrics | wc -l` (should be > 20)

### Weekly Checks

- [ ] Database growth normal: `du -sh /var/lib/postgresql/`
- [ ] Service restarts normal: `systemctl show dx-scraper --property=NRestarts`
- [ ] Disk space available: `df -h /`
- [ ] Memory usage stable: `ps aux | grep dx_cluster_live`

### Monthly Review

- [ ] Storage capacity sufficient
- [ ] Backup procedures working
- [ ] Documentation up-to-date
- [ ] Metrics historical data preserved

## Troubleshooting Verification

If issues occur, verify:

- [ ] Configuration file readable: `sudo -u dxcluster cat /etc/dxcluster/dxcluster.env`
- [ ] Database connection works: `sudo -u dxcluster psql -d dx_analysis -c "SELECT 1"`
- [ ] Metrics port accessible: `sudo ss -tlnp | grep 8000`
- [ ] Logs contain useful info: `sudo journalctl -u dx-scraper -n 50`

## Sign-Off

### Build Completed

- [x] Package successfully built
- [x] All dependencies resolved
- [x] Documentation complete
- [x] Deployment guides provided

### Ready for Deployment

- [ ] System prerequisites verified
- [ ] Package built successfully
- [ ] Configuration prepared
- [ ] Ready to install

### Installation Complete

- [ ] Package installed
- [ ] Service running
- [ ] Metrics flowing
- [ ] Database receiving data

---

**Checklist Version:** 2.0.0  
**Last Updated:** November 22, 2024  
**Status:** Ready for Deployment  
**Project:** CS 330 Homework 5 - Databases (Final Project)

## Next Actions

1. Review `DEPLOYMENT_PACKAGE_OVERVIEW.md`
2. Follow `SCRAPER_DEPLOYMENT_GUIDE.md` for complete deployment
3. Run build: `cd homework5/packages && ./build-scraper.sh`
4. Install package: `sudo dpkg -i dxcluster-scraper_2.0.0-1_all.deb`
5. Configure and start service
6. Monitor metrics and logs
7. Set up Prometheus/Grafana (optional but recommended)

## Support

For issues, check:
1. Logs: `sudo journalctl -u dx-scraper -f`
2. Metrics: `curl http://localhost:8000/metrics`
3. Configuration: `/etc/dxcluster/dxcluster.env`
4. Documentation: `homework5/SCRAPER_DEPLOYMENT_GUIDE.md`
