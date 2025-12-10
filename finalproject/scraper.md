# DX Scraper

The DX scraper is implemented as a [python script](../homework5/dx-scraper/dx_cluster_live_pg.py) that runs as a daemon on the
server via systemd.

It operates as a DX cluster client, reading the line-oriented protocol messages from the server and inserting records
into the database. It is configurable via a file in /etc.

The scraper is instrumented with prometheus hooks and status is in-turn scraped by Prometheus periodically.

The scraper is deployed as a Debian DPKG on the production server.

## Solar Reports

The DX scraper has the ability to parse DX cluster WWV solar reports an insert them into the database.

I also created a [standalone solar data scraper](../homework5/fetch_solar_data.py) to support the initial split-server deployment that I ended up using.

This script runs every 6 hours via cron and inserts into the same *wwv_announcements* table. 

This functionality will eventually be consolidated one way or another.
