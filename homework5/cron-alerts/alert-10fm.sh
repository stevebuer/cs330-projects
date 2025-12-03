#!/bin/bash

# crontab script fpr DX alerts

ALERTS=$(psql -d dx_analysis -f /home/steve/cron-alerts/10m-fm.sql --csv | grep -v time)

if [ ! -z $ALERTS ]; then

	echo $ALERTS | mail -s "10m FM Alert" steve@jxqz.org
	/home/steve/cron-alerts/voipms_sms.py 3609306443 2064576680 "$ALERTS"
fi
