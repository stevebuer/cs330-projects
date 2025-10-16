# Steve's Frequent Postgres Commands

Adding commands here used in configuration and debugging for quick reference.

Version: psql (PostgreSQL) 15.14 (Debian 15.14-0+deb12u1)

[Online Documentation for Postgres 15.14](https://www.postgresql.org/docs/15/index.html)

## Shell

* *psql -d dxcluster* to connect
* *createuser NAME*
* *dropuser NAME*

## psql client

* *\l* list databases
* *\d* list tables
* *select * from pg_roles;* to examine roles
* *\du* or *\dg* describe roles
* *\d TABLE* describe table
