-- DX Analysis cron alerts
--
-- 1. Recent 10m FM spots (29.6-29.7 MHz) (Pacific Time Zone)
--
SELECT 
    TO_CHAR(timestamp AT TIME ZONE 'America/Los_Angeles', 'HH24:MI') as time,
    dx_call,
    frequency,
    spotter_call,
    comment
FROM dx_spots
WHERE frequency BETWEEN 29600 AND 29700
    AND timestamp > NOW() - INTERVAL '15 minutes'
ORDER BY timestamp DESC;
