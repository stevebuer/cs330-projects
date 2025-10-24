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


