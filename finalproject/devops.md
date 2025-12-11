# DevOps Infrastructure

A fair amount of time and energy was put into getting the system deployed into a semi-production
environment and keeping it running. I think the current arrangement would best be described as a 
staging environment because a scalable production system would probably be fully containerized
such that is could be deployed into a Kubernetes cluster.

## VM Deploy and Upgrade

Two Linux virtual machines from Vultr were used for deployment. An existing system in New Jersey
and a newer dedicated machine in Seattle. The east coast machine had to be scaled to a larger
computer mid project. These systems will be consolidated as soon as is feasible.

## Hardware Upgrades

The development was done on an ageing Lenovo T440p laptop. Memory and CPU upgrades were performed on the development system
because it struggled to run some of the tools and sample projects at the beginning of the class. 

<img src="images/mem_cpu_upgrade.jpg" width="600">

Memory upgraded from 8GB to 16GB.

CPU upgraded from 2 core i5 CPU to 4 core i7.

Very noticeable difference in performance even for routine tasks.

## Overview of Technologies Used or Explored

A lot of software tools were explored during the course of this project. Not all made it in to the final system, or 
were used extensively for deployment. Here is a short list.

* Debian Linux for development and production systems
* PostgreSQL relational database
* Prometheus time-series database for metrics and monitoring
* Python for DX cluster scraper, API server, Dashboard
* Debian dpkg for deployment of dx-database and dx-scraper packages
* Scraper deamon control via systemctl
* Terraform was explored for provisioning, but not used extensively because the deployment remained simple
* Docker images were created for the API and Dashboard
* PlantUML was used for documentation the database schema
* OpenAPI yaml
* Streamlit for the dashboard
* Pytorch for ML model training and development
* Markdown for general documentation
* Git source control, and github actions for CI/CI, GHCR container repository
* Domain Name System (DNS) records for production services
* OpenAI API
* Voip.ms API

## Github Copilot

A large portion of project development was aided by Github copilot using the Claude Sonnet and Claude Haiku models.

AI-powered development is truly a game changer.
