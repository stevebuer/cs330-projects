-- DX Spot Alert SQL Examples
-- These queries can be used in cron jobs for monitoring and alerts

-- 1. Recent 10m FM spots (29.6-29.7 MHz)
SELECT 
    TO_CHAR(timestamp AT TIME ZONE 'America/Los_Angeles', 'HH24:MI') as time,
    dx_call,
    frequency,
    spotter_call,
    grid_square,
    comment
FROM dx_spots
WHERE frequency BETWEEN 29600 AND 29700
    AND timestamp > NOW() - INTERVAL '15 minutes'
ORDER BY timestamp DESC;

-- 2. Rare DX stations (spotted less than 5 times in last 7 days)
SELECT 
    dx_call,
    COUNT(*) as spot_count,
    MAX(timestamp) as last_seen,
    array_agg(DISTINCT frequency::text) as frequencies
FROM dx_spots
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY dx_call
HAVING COUNT(*) < 5
ORDER BY last_seen DESC;

-- 3. New stations (first time spotted in database)
SELECT DISTINCT ON (dx_call)
    dx_call,
    timestamp,
    frequency,
    spotter_call,
    grid_square
FROM dx_spots
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY dx_call, timestamp ASC;

-- 4. Specific callsign alert (replace 'K6XX' with target)
SELECT 
    timestamp,
    frequency,
    spotter_call,
    comment,
    band
FROM dx_spots
WHERE dx_call = 'K6XX'
    AND timestamp > NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC;

-- 5. High activity bands (more than 50 spots in last hour)
SELECT 
    band,
    COUNT(*) as spot_count,
    COUNT(DISTINCT dx_call) as unique_dx,
    MIN(frequency) as low_freq,
    MAX(frequency) as high_freq
FROM dx_spots
WHERE timestamp > NOW() - INTERVAL '1 hour'
    AND band IS NOT NULL
GROUP BY band
HAVING COUNT(*) > 50
ORDER BY spot_count DESC;

-- 6. Specific grid square activity
SELECT 
    timestamp,
    dx_call,
    frequency,
    spotter_call,
    comment
FROM dx_spots
WHERE grid_square LIKE 'CN87%'
    AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

-- 7. Band opening detection (sudden spike in activity)
WITH hourly_counts AS (
    SELECT 
        band,
        DATE_TRUNC('hour', timestamp) as hour,
        COUNT(*) as count
    FROM dx_spots
    WHERE timestamp > NOW() - INTERVAL '24 hours'
        AND band IS NOT NULL
    GROUP BY band, hour
)
SELECT 
    band,
    hour,
    count,
    LAG(count) OVER (PARTITION BY band ORDER BY hour) as prev_hour_count,
    count - LAG(count) OVER (PARTITION BY band ORDER BY hour) as increase
FROM hourly_counts
WHERE hour > NOW() - INTERVAL '2 hours'
ORDER BY increase DESC NULLS LAST
LIMIT 10;

-- 8. DX stations from specific country prefix
SELECT 
    dx_call,
    timestamp,
    frequency,
    band,
    spotter_call
FROM dx_spots
WHERE dx_call ~ '^(VK|ZL)[0-9]'  -- Australia/New Zealand
    AND timestamp > NOW() - INTERVAL '30 minutes'
ORDER BY timestamp DESC;

-- 9. Multi-band activity (same station on multiple bands)
SELECT 
    dx_call,
    COUNT(DISTINCT band) as band_count,
    array_agg(DISTINCT band ORDER BY band) as bands,
    COUNT(*) as total_spots,
    MAX(timestamp) as last_seen
FROM dx_spots
WHERE timestamp > NOW() - INTERVAL '2 hours'
GROUP BY dx_call
HAVING COUNT(DISTINCT band) >= 3
ORDER BY band_count DESC, last_seen DESC;

-- 10. Alert: Strong signal reports
SELECT 
    timestamp,
    dx_call,
    frequency,
    spotter_call,
    signal_report,
    comment
FROM dx_spots
WHERE signal_report ~ '^5[789]'  -- 57, 58, 59 reports
    AND timestamp > NOW() - INTERVAL '15 minutes'
ORDER BY timestamp DESC;
