#!/usr/bin/env bash
#
# This entrypoint file is adapted from
# https://github.com/puckel/docker-airflow

AIRFLOW_HOME="/opt/airflow"
CMD="airflow"
TRY_LOOP="10"
POSTGRES_HOST="airflow-postgres"
POSTGRES_PORT="5432"
RABBITMQ_HOST="airflow-rabbitmq"
RABBITMQ_CREDS="airflow:airflow"

# wait for DB
if [ "$1" = "webserver" ] || [ "$1" = "worker" ] || [ "$1" = "scheduler" ] ; then
  i=0
  echo "Checking for airflow database at $POSTGRES_HOST:$POSTGRES_PORT"
  while ! nc $POSTGRES_HOST $POSTGRES_PORT >/dev/null 2>&1 < /dev/null; do
    i=$((i+1))
    if [ $i -ge $TRY_LOOP ]; then
      echo "$(date) - ${POSTGRES_HOST}:${POSTGRES_PORT} still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for ${POSTGRES_HOST}:${POSTGRES_PORT}... $i/$TRY_LOOP"
    sleep 5
  done
  if [ "$1" = "webserver" ]; then
    echo "Initialize database..."
    $CMD initdb
  fi
  sleep 5
fi

if [ "$1" = "webserver" ] ; then
  echo "[program:airflow]" >> /etc/supervisor/conf.d/supervisord.conf
  echo "command=/usr/local/bin/airflow webserver -p 8080 -w 1" >> /etc/supervisor/conf.d/supervisord.conf
  cat /etc/supervisor/conf.d/supervisord.conf
fi

/usr/bin/supervisord
