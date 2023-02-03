#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

echo "Waiting for es"
while ! nc -z $ELASTIC_HOST $ELASTIC_PORT; do
      sleep 0.5
done

echo "ES is ready"

gunicorn -w 4 -k uvicorn.workers.UvicornH11Worker src.main:app --preload -b 0.0.0.0:8060