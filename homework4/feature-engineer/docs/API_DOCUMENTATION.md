# Ham Radio Spotting API Documentation

**API Source**: http://api.jxqz.org:8080/api/spots  
**Data**: Real-time ham radio spotting reports  
**Date**: November 7, 2025

---

## Overview

The Ham Radio Spotting API (RBN - Reverse Beacon Network) provides real-time data about radio spots from amateur radio operators worldwide. Each "spot" is a report of a detected radio transmission.

---

## Endpoint

### Get Spots
```
GET http://api.jxqz.org:8080/api/spots
```

**Purpose**: Retrieve recent radio spotting records

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | No | 100 | Maximum spots to return (1-1000) |
| `offset` | int | No | 0 | Number of records to skip |
| `band` | string | No | None | Filter by band (e.g., "20m", "40m") |
| `mode` | string | No | None | Filter by mode (CW, USB, SSB, LSB) |
| `callsign` | string | No | None | Filter by DX station callsign |

### Example Requests

```
# Get 100 most recent spots (default)
http://api.jxqz.org:8080/api/spots

# Get 500 spots
http://api.jxqz.org:8080/api/spots?limit=500

# Get 20m band only
http://api.jxqz.org:8080/api/spots?band=20m&limit=100

# Get CW mode only
http://api.jxqz.org:8080/api/spots?mode=CW&limit=100

# Skip first 50, get next 100
http://api.jxqz.org:8080/api/spots?offset=50&limit=100
```

---

## Response Format

### Success Response (HTTP 200)

```json
{
  "spots": [
    {
      "id": 123456,
      "timestamp": "Thu, 07 Nov 2025 17:08:35 GMT",
      "dx_call": "K1ABC",
      "spotter_call": "W2XYZ",
      "band": "20m",
      "frequency": "14075.900",
      "mode": "USB",
      "signal_report": "59",
      "snr": "15",
      "drift": "0",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "locator": "FN30",
      "comment": "loud signal",
      "url": "http://example.com"
    },
    {
      "id": 123457,
      "timestamp": "Thu, 07 Nov 2025 17:07:45 GMT",
      "dx_call": "VE3ABC",
      "spotter_call": "VE2XYZ",
      "band": "40m",
      "frequency": "7025.600",
      "mode": "CW",
      "signal_report": "569",
      "snr": "22",
      "drift": "0",
      "latitude": 43.6629,
      "longitude": -79.3957,
      "locator": "EN93",
      "comment": "very loud",
      "url": "http://example.com"
    }
  ],
  "total": 139847,
  "page": 1,
  "per_page": 100,
  "total_pages": 1399
}
```

### Error Response (HTTP 400)

```json
{
  "error": "Invalid parameter",
  "message": "Band parameter must be one of: 6m, 10m, 12m, 15m, 17m, 20m, 40m, 80m, 160m"
}
```

---

## Response Fields

### Spot Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | int | Unique spot identifier | 123456 |
| `timestamp` | string | Report time (UTC) | "Thu, 07 Nov 2025 17:08:35 GMT" |
| `dx_call` | string | Callsign being heard | "K1ABC" |
| `spotter_call` | string | Callsign reporting the spot | "W2XYZ" |
| `band` | string | Amateur radio band | "20m" |
| `frequency` | string | Exact frequency in kHz | "14075.900" |
| `mode` | string | Operating mode | "USB", "CW", "SSB", "LSB" |
| `signal_report` | string | Signal strength report | "59", "569" |
| `snr` | string | Signal-to-noise ratio (dB) | "15" |
| `drift` | string | Frequency drift (Hz) | "0" |
| `latitude` | float | Spotter latitude (degrees) | 40.7128 |
| `longitude` | float | Spotter longitude (degrees) | -74.0060 |
| `locator` | string | Grid square locator | "FN30" |
| `comment` | string | User comment | "loud signal" |
| `url` | string | Source URL | "http://example.com" |

---

## Data Types & Formats

### Timestamp Format
```
RFC 2822: "Thu, 07 Nov 2025 17:08:35 GMT"
Timezone: Always UTC (GMT)
Parse in Python: datetime.strptime(ts, "%a, %d %b %Y %H:%M:%S %Z")
```

### Band Values
```
6m, 10m, 12m, 15m, 17m, 20m, 40m, 80m, 160m
```

### Mode Values
```
CW   - Continuous Wave (Morse code)
USB  - Upper Single Sideband (voice)
LSB  - Lower Single Sideband (voice)
SSB  - Single Sideband (voice, not specified if USB/LSB)
FM   - Frequency Modulation
RTTY - Radio TeleTYpe
PSK  - Phase Shift Keying
FT8  - Digital mode
```

### Signal Report Format
```
RS(T) Format:
  R: Readability (1-5)
  S: Signal strength (1-9)
  T: Tone (1-9, CW only, optional)

Examples:
  "59"   = 5/9 (loud and clear)
  "569"  = 5/9 with good tone
  "449"  = 4/4/9 (readable, fair signal, good tone)
  ""     = Not reported (empty string)
```

### Coordinates
```
Latitude: -90.0 to +90.0 (S negative, N positive)
Longitude: -180.0 to +180.0 (W negative, E positive)
Example: New York = (40.7128, -74.0060)
```

### Grid Square (Maidenhead Locator)
```
Format: AABBCC or AABB
Example: FN30 (New York area)
Example: EN93VC (Toronto area)

Conversion:
  AA = Field (12x24 degrees, 20x10 deg zones)
  BB = Square (2x1 degree)
  CC = Subsquare (5x2.5 minutes, optional)
```

---

## Data Availability

### Current Status (As of Nov 7, 2025)

| Aspect | Details |
|--------|---------|
| **Data Range** | Real-time only (live reports) |
| **Historical Archive** | Not available via API |
| **Age of Data** | Most recent reports first |
| **Update Frequency** | Continuous (new reports as they arrive) |
| **Total Records** | 139,847+ cumulative |
| **Retention Period** | Unknown (varies by API implementation) |

### Important Notes

❌ **No Historical Data**: API returns only recent/current data  
❌ **No Date Filtering**: Cannot query by specific date  
❌ **No Pagination to Past**: Cannot go back in time systematically  
✅ **Real-time Only**: Best for monitoring current activity  
✅ **New Data**: Continuous updates as reports arrive  

---

## Limitations & Constraints

### Rate Limiting
```
Not documented - Assume reasonable limits
Recommended: 
  - Max 1-2 requests per second
  - Batch requests (limit=500 or 1000)
  - Cache results locally
```

### Request Size
```
Max limit: 1000 spots per request (typically)
Default: 100 spots
Larger limits may affect response time
```

### Response Size
```
Typical response: 50-200 KB per 100 spots
Large batches: May require streaming or pagination
```

### Timeout
```
Recommended timeout: 10-30 seconds
Network latency: ~100-500ms typical
```

---

## Supported Bands

The API includes 9 ham radio bands:

| Band | Frequency Range | Use |
|------|-----------------|-----|
| 6m | 50-54 MHz | VHF, short distance |
| 10m | 28-29.7 MHz | HF, propagation dependent |
| 12m | 24.89-24.99 MHz | HF, good propagation |
| 15m | 21-21.45 MHz | HF, daytime band |
| 17m | 18.068-18.168 MHz | HF, daytime propagation |
| 20m | 14-14.35 MHz | HF, popular band |
| 40m | 7-7.3 MHz | HF, night band |
| 80m | 3.5-4.0 MHz | HF, local, night |
| 160m | 1.8-2.0 MHz | HF, long distance |

---

## Common Use Cases

### 1. Real-time Activity Monitoring
```python
# Check current band activity
spots = fetch_api(limit=100)
activity_by_band = group_by_band(spots)
```

### 2. Signal Quality Analysis
```python
# Recent signal reports
spots = fetch_api(limit=500, mode='USB')
avg_signal = mean([parse_signal(s['signal_report']) for s in spots])
```

### 3. Propagation Patterns
```python
# Current propagation conditions
spots = fetch_api(limit=500)
by_band = group_by_band(spots)
for band, reports in by_band.items():
    print(f"{band}: {len(reports)} recent spots")
```

### 4. Daily Statistics
```python
# Collect all reports for a day (requires periodic polling)
# Note: Must call API repeatedly, as no date filter exists
spots_today = []
while True:
    spots = fetch_api(limit=100)
    today_spots = [s for s in spots if is_today(s['timestamp'])]
    spots_today.extend(today_spots)
    if len(today_spots) < 100:
        break  # No more today's spots
```

---

## Error Handling

### Common Errors

| HTTP Code | Error | Cause | Solution |
|-----------|-------|-------|----------|
| 200 | (none) | ✓ Success | Use response |
| 400 | Bad Request | Invalid parameter | Check parameter values |
| 401 | Unauthorized | Auth required | Add auth token if needed |
| 404 | Not Found | Endpoint wrong | Check URL |
| 429 | Too Many Requests | Rate limit exceeded | Wait before retrying |
| 500 | Server Error | API issue | Retry after delay |
| 503 | Service Unavailable | Maintenance | Check status page |

### Retry Strategy
```python
import time

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = urllib.request.urlopen(url, timeout=10)
            return response
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

---

## Implementation Notes

### Timestamp Parsing
```python
from datetime import datetime

timestamp_str = "Thu, 07 Nov 2025 17:08:35 GMT"
dt = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
date_key = dt.strftime("%Y-%m-%d")  # "2025-11-07"
```

### Frequency Conversion
```python
# API returns frequency as string in kHz
frequency_khz = "14075.900"  # string
frequency_mhz = float(frequency_khz) / 1000  # 14.0759 MHz
```

### Signal Report Parsing
```python
signal_str = "59"
if len(signal_str) >= 2:
    readability = int(signal_str[0])  # 5
    strength = int(signal_str[1])      # 9
elif len(signal_str) == 0:
    readability = strength = 0  # Not reported
```

---

## Performance Tips

### 1. Batch Requests
```python
# ✓ GOOD: Fetch 500 at once
spots = fetch_api(limit=500)

# ❌ POOR: Make 5 requests of 100 each
for i in range(5):
    spots = fetch_api(limit=100)
```

### 2. Local Caching
```python
# Cache results to avoid repeated API calls
last_fetch = None
cache = []

def get_spots():
    global last_fetch
    if time.time() - last_fetch > 60:  # Update every minute
        cache = fetch_api(limit=500)
        last_fetch = time.time()
    return cache
```

### 3. Filter Locally
```python
# ✓ GOOD: Fetch all, filter locally
spots = fetch_api(limit=500)
band_20m = [s for s in spots if s['band'] == '20m']

# ✗ POOR: Make separate API call
spots_20m = fetch_api(limit=100, band='20m')
```

### 4. Group by Date
```python
from collections import defaultdict
from datetime import datetime

spots = fetch_api(limit=500)
by_date = defaultdict(list)

for spot in spots:
    dt = datetime.strptime(spot['timestamp'], "%a, %d %b %Y %H:%M:%S %Z")
    date_key = dt.strftime("%Y-%m-%d")
    by_date[date_key].append(spot)
```

---

## Known Limitations

### ❌ What You CAN'T Do

1. **Query by date**: No way to request specific dates
2. **Historical data**: Only recent data available
3. **Authentication**: Not supported (public API)
4. **Webhooks**: No push notifications
5. **Streaming**: Must poll manually
6. **Sorting**: Results always newest first
7. **Complex filtering**: Limited to band/mode/callsign

### ✅ What You CAN Do

1. **Fetch recent reports**: Last N spots (up to 1000)
2. **Filter by band**: Get specific band
3. **Filter by mode**: Get CW/SSB/etc
4. **Filter by callsign**: Get specific station
5. **Batch process**: Fetch and filter locally
6. **Archive locally**: Store for analysis
7. **Aggregate**: Group by time/band/mode

---

## Troubleshooting

### "No data returned"
```
Causes:
  - API down or slow to respond
  - Network connectivity issue
  - Timeout too short
  
Solutions:
  - Check internet connection
  - Increase timeout (10+ seconds)
  - Retry with exponential backoff
  - Check http://api.jxqz.org:8080/api/spots in browser
```

### "Empty spots array"
```
Causes:
  - Filter too restrictive (band/mode/callsign)
  - API has no new data
  - All recent data matches filter
  
Solutions:
  - Try without filters
  - Increase limit parameter
  - Check if band is active (time of day)
```

### "Timestamp parsing error"
```
Causes:
  - Format string mismatch
  - Timezone not recognized
  
Solution:
  datetime.strptime(ts, "%a, %d %b %Y %H:%M:%S %Z")
```

### "Rate limited (429)"
```
Causes:
  - Too many requests too fast
  - API quota exceeded
  
Solutions:
  - Add delay between requests
  - Reduce request frequency
  - Batch larger requests (limit=500)
  - Implement exponential backoff
```

---

## Example Code

### Basic Usage
```python
import urllib.request
import json
from datetime import datetime

# Fetch spots
url = "http://api.jxqz.org:8080/api/spots?limit=100"
response = urllib.request.urlopen(url, timeout=10)
data = json.loads(response.read().decode('utf-8'))

# Process
for spot in data['spots']:
    print(f"{spot['dx_call']} on {spot['band']} "
          f"at {spot['timestamp']}")
```

### Aggregation
```python
from collections import defaultdict

url = "http://api.jxqz.org:8080/api/spots?limit=500"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))

# Group by date
by_date = defaultdict(list)
for spot in data['spots']:
    dt = datetime.strptime(spot['timestamp'], 
                          "%a, %d %b %Y %H:%M:%S %Z")
    date_key = dt.strftime("%Y-%m-%d")
    by_date[date_key].append(spot)

# Statistics per day
for date in sorted(by_date.keys()):
    spots = by_date[date]
    print(f"{date}: {len(spots)} spots")
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Type** | RESTful JSON API |
| **Base URL** | http://api.jxqz.org:8080/api/spots |
| **Data** | Real-time ham radio spots |
| **Auth** | None (public) |
| **Rate Limit** | Unknown (use reasonable throttling) |
| **Response Format** | JSON |
| **Max Records** | ~1000 per request |
| **Historical Data** | Not available |
| **Update Frequency** | Continuous |
| **Documentation** | This document |

---

## References

- **API Base**: http://api.jxqz.org:8080/api/spots
- **RBN Network**: Reverse Beacon Network
- **Ham Radio Bands**: https://en.wikipedia.org/wiki/Amateur_radio_frequency_allocations
- **Signal Reports**: RS(T) system
- **Grid Squares**: Maidenhead Locator System
