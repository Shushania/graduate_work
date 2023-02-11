#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

echo "Waiting for postgres"
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.5
done
echo "Postgres is ready"

# Для первого запуска
# ------
python manage.py migrate movies 0001 --fake
python manage.py migrate movies 0008
python manage.py migrate movies 0009 --fake
## Подгрузка фильмов, жанров и персон
python manage.py dump_films
# ------

# Миграции
python manage.py migrate
# Сохранение статики
python manage.py collectstatic --clear --noinput
# Запуск сервера
uwsgi --ini /etc/uwsgi.ini