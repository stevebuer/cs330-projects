# WWV Announcements - Implementation Notes

## Overview
The DX cluster scraper has been enhanced to detect and store WWV propagation announcements from NIST time stations.

## WWV Announcement Formats

WWV announcements typically come in two main formats:

### Format 1: Space-separated numbers (Legacy)
```
WWV de VE7CC:                   2100   14  73  14   0  0   0  0  0  0  0  0  0  0
```
Where the numbers represent:
- Solar Flux Index (SFI)
- A-index
- K-index
- Sunspot Number
- Additional propagation data

### Format 2: Key=value pairs (Modern)
```
WWV de W1AW:                    SFI=102 A=5 K=1 SSN=0
```
More readable format with explicit labels.

## Database Schema

The `wwv_announcements` table stores:

- **Solar Data**: SFI, A-index, K-index, sunspot number
- **Ionospheric Data**: X-ray flux, proton flux levels
- **Band Conditions**: Individual band propagation for 80m-10m
- **Storm Data**: Geomagnetic and solar radiation storm levels
- **Metadata**: Announcement type, parsing success flag

## Detection Logic

The scraper detects WWV announcements by:
1. Lines containing "WWV" (case-insensitive)
2. Lines starting with "WWV de " (standard format)

## Parsing Logic

The parser attempts multiple strategies:
1. **Numeric extraction**: Finds all numbers in space-separated format
2. **Key=value parsing**: Looks for SFI=, A=, K=, SSN= patterns
3. **Flexible assignment**: Maps found values to appropriate fields

## Storage

- Raw announcements are stored in the `raw_spots` table for consistency
- Parsed data goes into `wwv_announcements` with foreign key reference
- Parsing success is tracked for quality monitoring

## Usage Examples

### Query Recent WWV Data
```sql
SELECT timestamp, solar_flux, a_index, k_index, sunspot_number
FROM wwv_announcements
WHERE parsed_successfully = true
ORDER BY timestamp DESC
LIMIT 10;
```

### Monitor Parsing Success
```sql
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN parsed_successfully THEN 1 ELSE 0 END) as parsed,
    ROUND(100.0 * SUM(CASE WHEN parsed_successfully THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
FROM wwv_announcements;
```

### Solar Activity Trends
```sql
SELECT
    DATE(timestamp) as date,
    AVG(solar_flux) as avg_sfi,
    MAX(a_index) as max_a_index,
    AVG(sunspot_number) as avg_ssn
FROM wwv_announcements
WHERE parsed_successfully = true
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## Integration with DX Spots

WWV data can be correlated with DX spotting activity:

```sql
-- Spots during high solar activity
SELECT COUNT(*) as high_activity_spots
FROM dx_spots d
JOIN wwv_announcements w ON DATE(d.timestamp) = DATE(w.timestamp)
WHERE w.solar_flux > 150 AND w.parsed_successfully = true;
```

## Future Enhancements

- **Band condition parsing**: Extract detailed band-by-band propagation data
- **Storm level classification**: Parse geomagnetic storm categories (G1-G5)
- **Historical averaging**: Calculate running averages for trend analysis
- **Alert system**: Generate notifications for significant solar activity changes