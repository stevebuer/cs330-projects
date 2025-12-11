# System Monitoring

The monitoring system was borne of a series of performance and stability issues that arose during the
initial deployment of the database, scraper, and API server virtual machine. The first symptom was that
the scraper was getting stuck occasionally and data stopped flowing into the datbase. The API container
appeared to have intermitted trouble as well. The system was originally installed on an existing Linux
virtual machine that had been running for many years with a minimal load. 

Whatever the situation was, I wanted to have some kind of visibility into the status of the system and
what the conditions were leading up to any kind of stuck processes or other malfunctions.

I decided to install the [Prometheus time-series database](https://prometheus.io) and its companion
[Grafana](https://grafana.com). This allowed me to scrape performance metrics from the host operating
system, the Postgres database, and my daemon process that collected and stored DX spots.

I was able to see that the load average on the server was periodically become high and I would need to
allocate more resources. 

## DX Ingest Monitoring Dashbord

This dashboard is designed for system administration (DevOps) monitoring and will not be accessible to end users. In a 
typical production environment it would be behind a VPN or only accessible internally.

Note: Server uses a self-signed certificate so will give web browser warnings, but the connection is still encrypted.

Guest read-only account: cs330 / olympiccs

Server: [https://jersey.jxqz.org:3000](https://jersey.jxqz.org:3000)

A brief description of the monitoring sections follows.

### Host Status

Load average and memory usage charted over time. Instantaneous disk usage and memory utilization.

### Scraper Status

Spot rate and total spots. More metrics are available in Prometheus for future expansion of this section.

### Database Status

Last 5 spots in a table and total database size. 

### Web Servers and Container Status

Report status of ports and containers. Work in progress.

### Prototypes Queries

Playground for writing queries and prototyping with Grafana's powerful built-in visualizations.
