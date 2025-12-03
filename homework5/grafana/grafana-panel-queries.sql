-- These are some SQL queries created for Grafana visuals

-- 10m Band Status
SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END as value FROM dx_spots WHERE frequency BETWEEN 29600 AND 29700 AND timestamp >= DATE_TRUNC('day', CURRENT_TIMESTAMP AT TIME ZONE 'America/Los_Angeles') AT TIME ZONE 'America/Los_Angeles'

-- Maximum Observed Frequency (15 min)
SELECT 
    MAX(frequency) / 1000 as value
FROM dx_spots
WHERE timestamp > NOW() - INTERVAL '15 minutes'
    AND frequency BETWEEN 7000 AND 30000
