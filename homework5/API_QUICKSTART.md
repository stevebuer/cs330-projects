# DX Cluster API - Quick Start Guide

## Get Started in 5 Minutes

### 1. Health Check
```bash
curl http://localhost:8080/api/health
```
Expected: `{"status":"healthy","database":"connected"}`

### 2. View API Info
```bash
curl http://localhost:8080/api
```
Get an overview of all available endpoints.

### 3. Recent Activity
```bash
curl http://localhost:8080/api/spots/recent?limit=5
```
See the 5 most recent DX spots.

### 4. Band Statistics
```bash
curl http://localhost:8080/api/bands
```
View activity across all amateur radio bands.

### 5. Database Stats
```bash
curl http://localhost:8080/api/stats
```
Get comprehensive database statistics.

## Common Use Cases

### Monitor 20m Band Activity
```bash
curl "http://localhost:8080/api/spots?band=20m&limit=10"
```

### Find Most Active Stations
```bash
curl "http://localhost:8080/api/callsigns/top?limit=5"
```

### Real-time Monitoring
```bash
# Check for new spots every 30 seconds
watch -n 30 'curl -s "http://localhost:8080/api/spots/recent?limit=3" | jq ".spots[].dx_call"'
```

### Filter by Frequency
```bash
# 14.200-14.250 MHz (20m CW/Digital)
curl "http://localhost:8080/api/spots?frequency_min=14200&frequency_max=14250"
```

## Key Endpoints Summary

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/api/health` | Service status | Health monitoring |
| `/api/spots/recent` | Latest spots | Real-time activity |
| `/api/bands` | Band statistics | Band conditions |
| `/api/callsigns/top` | Most active stations | DXpedition tracking |
| `/api/stats` | Database summary | System metrics |

## Response Format

All endpoints return JSON with this structure:
```json
{
  "data": "...",
  "timestamp": "2025-10-17T21:10:40.835187",
  "status": "success"
}
```

## Parameters

Most endpoints support these common parameters:
- `limit`: Number of results (default: varies by endpoint)
- `hours`: Hours to look back (default: 24)
- `band`: Filter by band (10m, 15m, 20m, 40m, etc.)

For complete documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).
