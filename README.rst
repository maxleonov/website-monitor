Website Monitor
===============

A simple website monitor that saves website availability metrics to Postgres.


Overview
========

The solution consists of 2 main components:

* Website checker
   * periodically checks the target websites and sends the check results to Kafka
* Database writer
   * reads metrics from Kafka and saves them to Postgres DB


Highlights
==========

* asynchronous
* supports setting the check interval per target
* runs in docker containers


Supported metrics
=================

* http_response_time (float) - amount of time between sending the request and getting the response from the website, in seconds
* http_status (int) - HTTP response status the website responded with
* regexp_match (bool) - boolean indicating if the website response matched the regular expression


Data volume considerations
==========================

NOTE: Currently, the solution only stores the data.
It does not include any DB indexes which means it's not yet ready for querying.
That's something to be covered in the future development.
Adding DB indexes will increase the amount of data generated by the app and should be taken into account.

Given the data types used in the DB, and the following constraints:

* monitor 1000 websites
* use `check_interval_seconds=15`

... it's calculated that the app should generate approximately 4GB of data per month.


Requirements
============

* python 3.7+
* aiohttp
* aiokafka
* asyncpg
* protobuf


Quickstart
==========
* Copy example configs to start with::

      cp config/config.example.yml config/config.yml
      cp config/config.test.example.yml config/config.test.yml

* Edit `config/config.yml`, see "Configuration keys in config.yml" below for details
   * set Kafka bootstrap servers (`kafka` -> `bootstrap_servers`)
      * the current implementation uses SSL to connect to Kafka, and requires saving the SSL keys/certificates under `config/kafka/`
   * set Postgres URI (`postgres` -> `uri`)
   * add websites to monitor under `targets:`, see details below:
* Run the app, see "Running the monitor" section for details


Configuration
=============

The configuration is stored using the following structure::

  config
    ├── config.yml
    ├── config.test.yml
    ├── kafka
    │   ├── ca.pem
    │   ├── service.cert
    │   └── service.key


Configuration locations

* By default, the app uses the `./config/` folder
* The `config/` location can also be specified in `WEBSITE_MONITOR_CONFIG_PATH` environment variable

Configuration keys in `config.yml`

* `kafka`
   * `bootstrap_servers` (str, required) - list of Kafka bootstrap servers, in format `host1:port1,host2:port2,...`
* `postgres`
   * `uri` (str, required) - Postgres connection uri, in format `postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]`
* `targets`
   * `name` (str, required) - a unique target name that, up to 128 ASCII characters
   * `target` (str, required) - website URL
   * `check_interval_seconds` (int|float, required) - the number of seconds the monitor will wait before making the next check
   * `regexp` (str, optional) - a regular expression to check website content

Test configuration in `config/config.test.yml`
   * Note that the `targets` should stay empty. In any case they will be ignored during tests.


Running the monitor
===================

Run the application locally::

  make run


Running tests
=============

Run tests::

  make tests


License
=======

Apache Software License version 2.0 (see LICENSE for the full text of the license)


Project status
==============

The development of this app is on a very early stage, and still there are many topics to cover and issues to address.
I will paste below the list of TODOs that I have currently. That should give a realistic idea of what is currently missing:

* improve test coverage
* create test fixtures running kafka and postgres locally, in containers
* run kafka and postgres locally, in containers (currently the app fully depends them being created/set up externally)
* add terraform or equivalent to create resources the app depends on
* add db migrations
* add package versioning support
* reload configuration on SIGHUP
