# CS330 Final Project: DX Spotting Database Analysis

GITHUB COPILOT DO NOT MODIFY THIS FILE!!

The goal if this project was to collect real-time reports of long-distance amateur radio station contacts from a network of reporting 
servers and use the data set as a basis for predicting near-term future propagtion coditions.

## Overview of Technologies Used

* Debian Linux for development and production systems
* PostgreSQL relational database
* Prometheus time-series database for metrics and monitoring
* Python for DX cluster scraper, API server, Dashboard
* Debian dpkg for deployment of dx-database and dx-scraper packages
* Scraper deamon control via systemctl
* Terraform was explored for provisioning, but not used extensively because the deployment remained simple
* Docker images were created for the API and Dashboard
* PlantUML was used for documentation the database schema
* OpenAPI yaml?
* Streamlit for the dashboard
* Pytorch for ML model training and development
* Markdown for general documentation
* Git source control, and github actions for CI/CI, GHCR container repository
* Domain Name System (DNS) records for production services

## System Component Detail

### Development and Production Environments

The development was done on an ageing Lenovo T440p laptop. Memory and CPU upgrades were performed on the development system
because it struggled to run some of the tools and sample projects at the beginning of the class. The production environment
is a Linux (Debian bookworm) virtual machine hosted at Vultr. 

### DX Cluster Scraper

The essential component of this software systems is a continuously running Python script that connects to a DX Cluster server
and receives DX spots via a simple line-oriented format. The remote dx cluster server can also be configured with a server-side
filter to limit spots to frequencies of interest. The filter used for this projects was:

TODO

### Relational Database Server

The 

## Conclusions and Discussion

## References

* Books
