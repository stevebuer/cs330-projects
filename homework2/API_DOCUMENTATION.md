# DX Cluster REST API Documentation

## Overview

The DX Cluster REST API provides programmatic access to real-time amateur radio DX cluster spot data. The API serves data from a PostgreSQL database that is continuously updated with spots from DX cluster networks.

## Base URL

```
http://localhost:8080/api
```

## Authentication

Currently, the API is read-only and does not require authentication.

## Response Format

All responses are in JSON format with the following structure:

```json
{
  "data": "...",
  "timestamp": "2025-10-17T21:10:40.835187",
  "status": "success"
}
```

Error responses include:
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Endpoints

### Health Check

**GET** `/api/health`

Returns the health status of the API and database connection.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Status Codes:**
- `200` - Service healthy
- `500` - Service unhealthy (database disconnected)

---

### API Information

**GET** `/api`

Returns API metadata and available endpoints.

**Response:**
```json
{
  "name": "DX Cluster API",
  "description": "REST API for DX cluster spot data",
  "version": "1.0.0",
  "timestamp": "2025-10-17T21:09:29.679809",
  "endpoints": {
    "health": "/api/health - Health check",
    "stats": "/api/stats - Basic database statistics",
    "spots": "/api/spots - Get spots with filtering options",
    "recent_spots": "/api/spots/recent - Get recent spots",
    "bands": "/api/bands - Get band information",
    "frequency_histogram": "/api/frequency/histogram - Frequency distribution",
    "hourly_activity": "/api/activity/hourly - Hourly activity stats",
    "top_callsigns": "/api/callsigns/top - Top active callsigns"
  }
}
```

---

### Database Statistics

**GET** `/api/stats`

Returns comprehensive database statistics including totals and recent activity.

**Response:**
```json
{
  "timestamp": "2025-10-17T21:09:34.837602",
  "total": {
    "total_spots": 737,
    "unique_dx_stations": 393,
    "unique_spotters": 376,
    "earliest_spot": "Fri, 17 Oct 2025 09:17:55 GMT",
    "latest_spot": "Sat, 18 Oct 2025 00:26:26 GMT"
  },
  "today": {
    "spots_today": 737,
    "dx_stations_today": 393,
    "spotters_today": 376
  },
  "recent": {
    "spots_last_hour": 667,
    "active_spotters": 336
  }
}
```

---

### DX Spots

**GET** `/api/spots`

Returns DX spots with optional filtering and pagination.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of spots to return (default: 50, max: 500)
- `offset` (integer, optional): Number of spots to skip for pagination (default: 0)
- `band` (string, optional): Filter by amateur radio band (e.g., "20m", "40m")
- `frequency_min` (float, optional): Minimum frequency in kHz
- `frequency_max` (float, optional): Maximum frequency in kHz
- `dx_call` (string, optional): Filter by DX station callsign
- `spotter_call` (string, optional): Filter by spotter callsign
- `mode` (string, optional): Filter by operating mode (e.g., "CW", "SSB", "FT8")
- `since` (string, optional): ISO datetime string for minimum spot time
- `until` (string, optional): ISO datetime string for maximum spot time

**Example Request:**
```
GET /api/spots?band=20m&frequency_min=14000&frequency_max=14350&limit=10&mode=CW
```

**Response:**
```json
{
  "spots": [
    {
      "id": 752,
      "timestamp": "Sat, 18 Oct 2025 00:26:26 GMT",
      "dx_call": "VE9CF",
      "frequency": "28429.000",
      "spotter_call": "OH0M-44",
      "comment": "WWFF VEFF-3332",
      "mode": null,
      "signal_report": null,
      "grid_square": null,
      "band": "10m"
    }
  ],
  "count": 1,
  "total_available": 218,
  "filters_applied": {
    "band": "20m",
    "mode": "CW"
  },
  "timestamp": "2025-10-17T21:15:00.000000"
}
```

---

### Recent Spots

**GET** `/api/spots/recent`

Returns the most recent DX spots from the last 24 hours.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of spots to return (default: 20, max: 100)
- `hours` (integer, optional): Hours to look back (default: 24, max: 168)

**Example Request:**
```
GET /api/spots/recent?limit=5&hours=6
```

**Response:**
```json
{
  "spots": [
    {
      "id": 752,
      "timestamp": "Sat, 18 Oct 2025 00:26:26 GMT",
      "dx_call": "VE9CF",
      "frequency": "28429.000",
      "spotter_call": "OH0M-44",
      "comment": "WWFF VEFF-3332",
      "mode": null,
      "signal_report": null,
      "grid_square": null,
      "band": "10m"
    }
  ],
  "count": 3,
  "hours": 6,
  "timestamp": "2025-10-17T21:09:49.747534"
}
```

---

### Band Information

**GET** `/api/bands`

Returns activity statistics for all amateur radio bands.

**Response:**
```json
{
  "bands": [
    {
      "band": "10m",
      "spot_count": 218,
      "dx_stations": 113,
      "min_freq": "28004.200",
      "max_freq": "29600.000",
      "latest_spot": "Sat, 18 Oct 2025 00:26:26 GMT"
    },
    {
      "band": "20m",
      "spot_count": 103,
      "dx_stations": 68,
      "min_freq": "14010.000",
      "max_freq": "14343.000",
      "latest_spot": "Sat, 18 Oct 2025 00:26:14 GMT"
    }
  ],
  "timestamp": "2025-10-17T21:10:30.193248"
}
```

---

### Frequency Histogram

**GET** `/api/frequency/histogram`

Returns frequency distribution data for creating histograms and frequency analysis.

**Query Parameters:**
- `bins` (integer, optional): Number of histogram bins (default: 50, max: 200)
- `band` (string, optional): Filter by specific band
- `hours` (integer, optional): Hours to look back (default: 24)

**Example Request:**
```
GET /api/frequency/histogram?band=20m&bins=20
```

**Response:**
```json
{
  "histogram": [
    {
      "frequency_range": "14000.0-14020.0",
      "count": 15,
      "center_freq": 14010.0
    },
    {
      "frequency_range": "14020.0-14040.0", 
      "count": 23,
      "center_freq": 14030.0
    }
  ],
  "band": "20m",
  "total_spots": 103,
  "bins": 20,
  "timestamp": "2025-10-17T21:15:00.000000"
}
```

---

### Hourly Activity

**GET** `/api/activity/hourly`

Returns spot activity broken down by hour of the day.

**Query Parameters:**
- `hours` (integer, optional): Hours of historical data to analyze (default: 24, max: 168)
- `timezone` (string, optional): Timezone for hour calculation (default: UTC)

**Example Request:**
```
GET /api/activity/hourly?hours=48
```

**Response:**
```json
{
  "hourly_activity": [
    {
      "hour": 0,
      "spot_count": 45,
      "unique_dx": 23,
      "unique_spotters": 18
    },
    {
      "hour": 1,
      "spot_count": 38,
      "unique_dx": 19,
      "unique_spotters": 15
    }
  ],
  "hours_analyzed": 48,
  "timezone": "UTC",
  "timestamp": "2025-10-17T21:15:00.000000"
}
```

---

### Top Callsigns

**GET** `/api/callsigns/top`

Returns the most active DX stations and spotters.

**Query Parameters:**
- `limit` (integer, optional): Number of callsigns to return for each category (default: 10, max: 50)
- `hours` (integer, optional): Hours to look back (default: 24, max: 168)

**Example Request:**
```
GET /api/callsigns/top?limit=5&hours=12
```

**Response:**
```json
{
  "top_spotted": [
    {
      "callsign": "5K0UA",
      "times_spotted": 18,
      "spotted_by": 16,
      "last_spotted": "Sat, 18 Oct 2025 00:23:26 GMT"
    },
    {
      "callsign": "S51DX",
      "times_spotted": 15,
      "spotted_by": 13,
      "last_spotted": "Sat, 18 Oct 2025 00:25:56 GMT"
    }
  ],
  "top_spotters": [
    {
      "callsign": "IZ1ABC",
      "spot_count": 25,
      "stations_spotted": 11,
      "last_activity": "Sat, 18 Oct 2025 00:23:54 GMT"
    },
    {
      "callsign": "OH0M-44",
      "spot_count": 22,
      "stations_spotted": 9,
      "last_activity": "Sat, 18 Oct 2025 00:26:26 GMT"
    }
  ],
  "timestamp": "2025-10-17T21:10:40.835187"
}
```

## Data Types

### Spot Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique spot identifier |
| `timestamp` | string | ISO datetime when spot was created |
| `dx_call` | string | Callsign of the DX station being spotted |
| `frequency` | string | Operating frequency in kHz |
| `spotter_call` | string | Callsign of the station reporting the spot |
| `comment` | string | Additional information about the spot |
| `mode` | string\|null | Operating mode (CW, SSB, FT8, etc.) |
| `signal_report` | string\|null | Signal strength report |
| `grid_square` | string\|null | Maidenhead grid square |
| `band` | string | Amateur radio band (10m, 20m, etc.) |

### Band Object

| Field | Type | Description |
|-------|------|-------------|
| `band` | string | Amateur radio band designation |
| `spot_count` | integer | Total spots in this band |
| `dx_stations` | integer | Unique DX stations spotted |
| `min_freq` | string | Lowest frequency spotted (kHz) |
| `max_freq` | string | Highest frequency spotted (kHz) |
| `latest_spot` | string | Timestamp of most recent spot |

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (endpoint doesn't exist)
- `500` - Internal Server Error (database/server issue)

### Error Response Format

```json
{
  "error": "Bad Request",
  "message": "Invalid parameter: limit must be between 1 and 500"
}
```

### Common Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Database connection failed` | Cannot connect to PostgreSQL | Check database connectivity |
| `Invalid parameter` | Query parameter validation failed | Check parameter types and ranges |
| `Resource not found` | Requested endpoint doesn't exist | Check endpoint URL |

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting based on your usage requirements.

## Examples

### Get Recent 20m CW Activity

```bash
curl "http://localhost:8080/api/spots?band=20m&mode=CW&limit=20"
```

### Monitor Real-time Activity

```bash
# Get latest spots every 30 seconds
while true; do
  curl "http://localhost:8080/api/spots/recent?limit=5"
  sleep 30
done
```

### Generate Band Activity Report

```bash
# Get comprehensive band statistics
curl "http://localhost:8080/api/bands" | jq '.'
```

### Find Top DX Activity

```bash
# Get most active stations in last 6 hours
curl "http://localhost:8080/api/callsigns/top?hours=6&limit=10"
```

## Integration Examples

### Python

```python
import requests
import json

# Get recent spots
response = requests.get('http://localhost:8080/api/spots/recent')
spots = response.json()

for spot in spots['spots']:
    print(f"{spot['dx_call']} on {spot['frequency']} spotted by {spot['spotter_call']}")
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function getRecentSpots() {
    const response = await fetch('http://localhost:8080/api/spots/recent');
    const data = await response.json();
    return data.spots;
}
```

### Bash/Shell

```bash
#!/bin/bash
# Simple spot monitoring script
curl -s "http://localhost:8080/api/spots/recent?limit=5" | \
  jq -r '.spots[] | "\(.dx_call) on \(.frequency) (\(.band))"'
```

## WebSocket Support

Currently, the API provides REST endpoints only. For real-time updates, consider polling the `/api/spots/recent` endpoint or implementing WebSocket support in future versions.

## Data Freshness

Spot data is updated in real-time as new spots are received from the DX cluster network. The `timestamp` field in each response indicates when the data was retrieved from the database.

## Support

For questions or issues with the API, please refer to the project documentation or submit an issue to the project repository.