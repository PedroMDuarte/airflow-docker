### Docker-compose

The `docker-compose.yml` file defines the services that will be provisioned.
The airflow webserver, scheduler, and worker services are nearly the same,
so they are derived from a single imaged tagged as `airflow-docker`.

#### Build `airflow-docker` image

From the repo's `docker` folder do:

    $ docker build -t airflow-docker .

#### Build and bring up services

    $ docker-compose up --build

After the webserver container is up and running, we can use it to initialize
airflow's database:

    $ docker exec -ti airflow-webserver airflow initdb

The connections to external data services can be setup by running the following
command:

    $ docker exec -ti airflow-webserver /opt/altx_airflow/bin/setup_airflow_connections.py
