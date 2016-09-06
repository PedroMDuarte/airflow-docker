# Airflow in Docker

This repo provides the Docker files necessary to run Apache Airflow (with the
CeleryExecutor) using Docker containers for each of the following services:

- postgres
- rabbitmq
- airflow webserver
- airflow scheduler
- airflow worker

The configuration for Airflow can be found in `conf/airflow.cfg`.

The goal of this project is to provide an easy way to get up and running
with airflow.  This may help people that are trying out the project for the
first time and may also help airflow developers that need a simple deployment
to test out new features.

I also recommend you take a look at https://github.com/puckel/docker-airflow.

### Docker-compose

The `docker-compose.yml` file defines the services that will be provisioned.
The airflow webserver, scheduler, and worker services are nearly the same,
so they are derived from a single imaged tagged as `airflow-docker`.

#### Step 1. Build `airflow-docker` image

    $ docker build -rm -t airflow-docker .

#### Step 2. Bring up services

    $ docker-compose up
