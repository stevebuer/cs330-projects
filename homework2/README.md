# CS330 Homework 2 Project Development

My goal in this iteration is to move the project from a proof-of-concept/prototype stage to a pre-alpha working system deployed into a production environment.

## Initial list of features for this iteration

These are the list of features or goals that I have considered for implementing. I will preserve this to-do list here and then document the work in a section below.
Anything remaining will need to be pushed to the next iteration or re-factored.

* Configure DNS with server name: dx.jxqz.org
* Configure Apache Web Server to support this virtual host.
* Install Postgres server into production environment and configure users and access control.
* Migrate (or create) database schema for Postgres.
* Rewrite the dx cluster scraping program to have:
   * Fault tolerance and error handling
   * Stop, Start, Status Control interface for the web API to hook to
   * Logging of status error conditions to syslog or similar
   * Options for: raw storage of data to text file or database insert
   * Packaging and Deployment mechanism
* Initial pass of a Web UI control panel in the style of a monitoring dashboard (for now)
* Updated Schema Documentaion
* Chat Logs and the Usual
* SQL quick reference and study guide
* Consider a deployment strategy: packages, containers, etc?
* CI/CD pipline and automated testing?

## Development Tasks

### DNS Configuration

I no longer run my own DNS server. I will need to add an entry through my domain registrar I think.

hostname: dx.jxqz.org

### Configure Apache virtual server

I have an existing Linux virtual machine that runs my website and email.
