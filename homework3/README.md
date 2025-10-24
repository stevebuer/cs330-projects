# CS 330 Homework 3

Third iteration on DX Predictor Project.

## Todo List

* Another scraper data source
* Is there additional meta-data I need to create or extract to characterize a DX path?
	* Average, Max Distance propagated?
	* Observed MUF.
* Data Filtering: WSPR, Weaks signal crap ignore.
* Exclude 2 meter spots from DX cluster reports
* Create list of Steve's Personal Predictors (SPP) to watch
* Data mining? 
* What ML models can be developed?
* Add user login to Dash.
* Try another dashboard besides dash
* Sysadmin work to get space for container deploy
* Documentation on joins and join tables. Sqlite sample db for examples.
* Add automated test cases?
* Alerting infrastructure
* Configure AR-Cluster Filters: YAML FILE?
* Store WWV Reports

## Store WWV Announcements in database

<pre>
   Date     Hour  SFI   A   K   Forecast
24-Oct-2025 00    130   6   2   No Storms -> No Storms                 <VE7CC>
23-Oct-2025 21    130   5   2   No Storms -> No Storms                 <AE5E>
23-Oct-2025 18    133   4   1   No Storms -> No Storms                 <W0MU>
23-Oct-2025 15    133   4   1   No Storms -> No Storms                 <VE7CC>
23-Oct-2025 12    133   4   1   No Storms -> No Storms                 <AE5E>
</pre>

## Done

### Namespace Adjustments

I renamed the database to reflect because I want to be able to bring in other data sources and other types of data such as user info.

*sudo systemctl stop dx-scraper*
<pre>
psql -d postgres
postgres=# ALTER DATABASE dxcluster RENAME TO dx_analysis;
</pre>
Update database name in /etc/dxcluster/dxcluster.env

*sudo systemctl start dx-scraper*

