#!/bin/bash
#
# 10m FM Alert with SMS notification via VoIP.ms
# Checks for 10m FM activity and sends SMS if spots found
#

# Database connection (customize as needed)
DB_HOST="your-db-host"
DB_USER="dx_user"
DB_NAME="dx_cluster"

# VoIP.ms Settings (configure these)
VOIPMS_DID="2065551234"          # Your VoIP.ms phone number
DESTINATION="2065559876"          # Phone number to send alerts to

# Path to SMS script
SCRIPT_DIR="$(dirname "$0")"
SMS_SCRIPT="$SCRIPT_DIR/voipms_sms.py"

# Query for 10m FM activity today (Seattle time)
SQL_QUERY="SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END as value FROM dx_spots WHERE frequency BETWEEN 29600 AND 29700 AND timestamp >= DATE_TRUNC('day', CURRENT_TIMESTAMP AT TIME ZONE 'America/Los_Angeles') AT TIME ZONE 'America/Los_Angeles'"

# Run query
RESULT=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "$SQL_QUERY" | tr -d ' ')

# Check if 10m FM is open
if [ "$RESULT" = "1" ]; then
    # Get spot count for message
    COUNT_QUERY="SELECT COUNT(*) FROM dx_spots WHERE frequency BETWEEN 29600 AND 29700 AND timestamp >= DATE_TRUNC('day', CURRENT_TIMESTAMP AT TIME ZONE 'America/Los_Angeles') AT TIME ZONE 'America/Los_Angeles'"
    SPOT_COUNT=$(psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -t -c "$COUNT_QUERY" | tr -d ' ')
    
    # Send SMS alert
    MESSAGE="10m FM is OPEN! ${SPOT_COUNT} spots detected today in 29.6-29.7 MHz"
    python3 "$SMS_SCRIPT" "$VOIPMS_DID" "$DESTINATION" "$MESSAGE"
    
    if [ $? -eq 0 ]; then
        echo "$(date): SMS alert sent - 10m FM open with $SPOT_COUNT spots"
    else
        echo "$(date): ERROR - Failed to send SMS alert" >&2
    fi
else
    echo "$(date): No 10m FM activity detected today"
fi
