# DX Cluster Live Scraper - Prometheus Integration

## Prometheus Metrics

The DX scraper now exports metrics in Prometheus format on port 8000 by default.

### Available Metrics

#### Counters (monotonically increasing)
- `dx_scraper_spots_total` - Total DX spots received (labeled by band and mode)
- `dx_scraper_spots_stored_total` - Total spots successfully stored (labeled by band and mode)
- `dx_scraper_spots_filtered_total` - Total spots filtered out (labeled by reason)
- `dx_scraper_wwv_total` - Total WWV announcements received
- `dx_scraper_wwv_stored_total` - Total WWV announcements stored
- `dx_scraper_db_errors_total` - Total database errors
- `dx_scraper_connection_errors_total` - Total connection errors to DX cluster

#### Gauges (point-in-time values)
- `dx_scraper_lines_received_total` - Total lines received from cluster
- `dx_scraper_spots_received` - Spots received since scraper start
- `dx_scraper_uptime_seconds` - Scraper uptime in seconds
- `dx_scraper_last_spot_timestamp` - Timestamp of last received spot (Unix epoch)
- `dx_scraper_cluster_connected` - 1 if connected to cluster, 0 if disconnected

#### Histograms (latency/duration)
- `dx_scraper_db_insert_seconds` - Database insert latency in seconds

## Configuration

Set environment variables to configure metrics:

```bash
# Enable/disable metrics server (default: true)
METRICS_ENABLED=true

# Metrics server port (default: 8000)
METRICS_PORT=8000
```

## Usage

### Start the scraper with metrics

```bash
# Default mode (quiet, metrics on port 8000)
./dx_cluster_live_pg.py

# With verbose logging
./dx_cluster_live_pg.py -v

# With debug logging
./dx_cluster_live_pg.py -d
```

### Query metrics

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Get specific metric
curl http://localhost:8000/metrics | grep dx_scraper_spots_stored_total
```

### Prometheus Configuration

Add this scrape job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'dx-scraper'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    scrape_timeout: 10s
```

## Grafana Dashboard

Key metrics to visualize in Grafana:

1. **Ingestion Rate** - `rate(dx_scraper_spots_stored_total[5m])`
2. **Spots by Band** - `dx_scraper_spots_stored_total{}`
3. **Connection Status** - `dx_scraper_cluster_connected`
4. **Scraper Uptime** - `dx_scraper_uptime_seconds / 3600` (in hours)
5. **Database Insert Latency** - `histogram_quantile(0.95, dx_scraper_db_insert_seconds_bucket)`
6. **Total Errors** - `rate(dx_scraper_db_errors_total[5m]) + rate(dx_scraper_connection_errors_total[5m])`

## Alerts

Example alert rules for `prometheus/alerts.yml`:

```yaml
groups:
  - name: dx_scraper
    rules:
      - alert: DXScraperDown
        expr: dx_scraper_cluster_connected == 0
        for: 5m
        annotations:
          summary: "DX Scraper disconnected from cluster"

      - alert: DXScraperHighErrorRate
        expr: rate(dx_scraper_db_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "DX Scraper database error rate high"

      - alert: DXScraperLowIngestionRate
        expr: rate(dx_scraper_spots_stored_total[5m]) < 0.1
        for: 10m
        annotations:
          summary: "DX Scraper ingestion rate is very low"
```

## Troubleshooting

### Metrics not appearing
- Check if `METRICS_ENABLED=true` is set
- Verify port `METRICS_PORT` is accessible: `telnet localhost 8000`
- Check logs for "Prometheus metrics server started" message

### High latency metrics
- `dx_scraper_db_insert_seconds` shows database insert time
- High values may indicate database performance issues

### Connection drops
- Monitor `dx_scraper_connection_errors_total`
- Use alert to trigger automatic restart via systemd
