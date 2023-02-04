#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

echo "Waiting for postgres"
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.5
done

echo "Postgres is ready"

echo "Waiting for es"
while ! nc -z $ELASTIC_HOST $ELASTIC_PORT; do
      sleep 0.5
done

echo "ES is ready"

echo "Waiting for redis"
while ! nc -z $BROKER_HOST $BROKER_PORT; do
      sleep 0.5
done

echo "Redis is ready"

python main.py