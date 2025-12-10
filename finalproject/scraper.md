# DX Scraper

The DX scraper is implemented as a [python script](../homework5/dx-scraper/dx_cluster_live_pg.py) that runs as a daemon on the
server via systemd.

It operates as a DX cluster client, reading the line-oriented protocol messages from the server and inserting records
into the database. It is configurable via a file in /etc.

The scraper is instrumented with prometheus hooks and status is in-turn scraped by Prometheus periodically.

The scraper is deployed as a Debian DPKG on the production server.
