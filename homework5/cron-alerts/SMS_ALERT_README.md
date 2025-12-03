# VoIP.ms SMS Alert Configuration

## Setup Instructions

### 1. Get VoIP.ms API Credentials

1. Log into your VoIP.ms account
2. Go to **Main Menu** → **API**
3. Enable API access if not already enabled
4. Note your API username and password

### 2. Configure Environment Variables

Create a `.env` file or add to your existing one:

```bash
# VoIP.ms API Credentials
VOIPMS_API_USER="your_api_username"
VOIPMS_API_PASSWORD="your_api_password"
```

Or export directly in your shell profile:

```bash
export VOIPMS_API_USER="your_api_username"
export VOIPMS_API_PASSWORD="your_api_password"
```

### 3. Configure Alert Script

Edit `alert-10fm-sms.sh` and update:

```bash
# Your VoIP.ms DID (the phone number to send FROM)
VOIPMS_DID="2065551234"

# Destination phone number (where to send alerts)
DESTINATION="2065559876"

# Database connection
DB_HOST="your-db-host"
DB_USER="dx_user"
DB_NAME="dx_cluster"
```

### 4. Make Scripts Executable

```bash
chmod +x voipms_sms.py
chmod +x alert-10fm-sms.sh
```

### 5. Test SMS Sending

```bash
# Test the SMS module directly
./voipms_sms.py 2065551234 2065559876 "Test message from DX alerts"
```

### 6. Test Alert Script

```bash
# Run the full alert script
./alert-10fm-sms.sh
```

### 7. Add to Crontab

Run every 15 minutes during daytime hours (8am-6pm Pacific):

```cron
# Check for 10m FM activity every 15 minutes
*/15 8-18 * * * /home/steve/GITHUB/cs330-projects/homework5/cron-alerts/alert-10fm-sms.sh >> /var/log/dx-alerts.log 2>&1
```

Install with:

```bash
crontab -e
```

## API Reference

### VoIP.ms sendSMS Method

**Endpoint:** `https://voip.ms/api/v1/rest.php`

**Parameters:**
- `api_username` - Your API username
- `api_password` - Your API password
- `method` - Set to "sendSMS"
- `did` - Your VoIP.ms DID (phone number)
- `dst` - Destination phone number (10 digits)
- `message` - SMS message content (160 chars per segment)

**Response:**
```json
{
  "status": "success",
  "sms": "12345678"
}
```

## Usage Examples

### Send SMS from Python

```python
from voipms_sms import send_sms

result = send_sms(
    did="2065551234",
    destination="2065559876",
    message="10m FM is open!"
)

if result['status'] == 'success':
    print(f"SMS sent! ID: {result['sms_id']}")
```

### Send SMS from Command Line

```bash
./voipms_sms.py 2065551234 2065559876 "Alert: 10m FM activity detected!"
```

### Integration with Database Query

```bash
# Query database and send result
SPOTS=$(psql -t -c "SELECT COUNT(*) FROM dx_spots WHERE frequency BETWEEN 29600 AND 29700")
./voipms_sms.py 2065551234 2065559876 "10m FM: $SPOTS spots today"
```

## Troubleshooting

### API Authentication Errors

- Verify API is enabled in VoIP.ms account
- Check username/password are correct
- Ensure no extra spaces in credentials

### SMS Not Sending

- Verify DID is active in your VoIP.ms account
- Check DID has SMS capability enabled
- Ensure destination number is valid (10 digits for US/Canada)
- Check account balance for SMS credits

### Database Connection Issues

- Verify database host, user, and credentials
- Test connection: `psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"`
- Check firewall rules if connecting to remote database

### Cron Job Not Running

- Check cron logs: `grep CRON /var/log/syslog`
- Verify script paths are absolute
- Ensure environment variables are loaded
- Test script manually first

## Cost Considerations

VoIP.ms SMS rates (as of 2025):
- **Outbound SMS:** ~$0.01 per message segment
- **Message segments:** 160 characters per segment

Example costs:
- 100 alerts/month = ~$1.00
- Daily alert during active season = ~$0.30/month

## Rate Limiting

To avoid alert spam:

```bash
# Only send once per day when band opens
ALERT_FILE="/tmp/10m-fm-alert-sent-$(date +%Y%m%d)"

if [ "$RESULT" = "1" ] && [ ! -f "$ALERT_FILE" ]; then
    # Send SMS
    touch "$ALERT_FILE"
fi
```

## Advanced Usage

### Multiple Band Alerts

Create separate scripts for different bands:
- `alert-10m-sms.sh` - 10m FM (29.6-29.7)
- `alert-6m-sms.sh` - 6m FM (52.0-54.0)
- `alert-dxcc-sms.sh` - Rare DXCC entities

### Conditional Alerts

Only alert for specific conditions:

```sql
-- Only alert for rare grids
SELECT COUNT(*) FROM dx_spots 
WHERE frequency BETWEEN 29600 AND 29700 
AND grid_square LIKE 'DN%'  -- Rare Alaska grids
AND timestamp >= NOW() - INTERVAL '15 minutes'
```
