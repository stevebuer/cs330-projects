#!/bin/bash

# crontab script fpr DX alerts

ALERTS=$(psql -f 10m-fm.sql --csv | grep -v time)

if [ ! -z $ALERTS ]; then

	echo $ALERTS | mail -s "10m FM Alert" steve@jxqz.org
fi
