import logging
from contextlib import contextmanager
from datetime import datetime
from time import sleep

import psycopg2
from decorator import backoff
from elasticsearch import Elasticsearch
from es_load import ES_LOAD
from etl_redis import ETLRedis
from index import INDEXES as index_body
from pg_dump import PG_DUMP
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from settings import Settings


@contextmanager
def conn_context_es(host: str, port: str):
    """
    Подключение к es
    """

    @backoff(logger=logging.getLogger('main::conn_context_es'))
    def connect(host: str, port: str):
        conn = Elasticsearch(f"{host}://{host}:{port}")
        return conn

    conn = connect(host, port)
    yield conn


@contextmanager
def conn_context_postgres(dsl: dict):
    """
    Подключение к postgres
    """

    @backoff(logger=logging.getLogger('main::conn_context_postgres'))
    def connect(dsl: dict):
        conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
        return conn

    conn = connect(dsl)
    yield conn


def postgres_to_es(es_conn: Elasticsearch, pg_conn: _connection):
    """
    Основной скрипт по выгрузке данных в es
    """
    redis = ETLRedis()
    pg_dump = PG_DUMP(pg_conn)
    es_load = ES_LOAD(es_conn)
    for item in range(len(settings.elastic_index)):
        lasttime = redis.get_lasttime(settings.elastic_index[item])
        for ids in pg_dump.get_updated_id(item, lasttime):
            entity = pg_dump.get_by_id(item, ids)
            es_load.create_index(item)
            es_load.bulk_update(item, entity)
            redis.set_lasttime(settings.elastic_index[item], datetime.now())


if __name__ == '__main__':
    settings = Settings()
    dsl = {
        'dbname': settings.postgres_name,
        'user': settings.postgres_user,
        'password': settings.postgres_password,
        'host': settings.postgres_host,
        'port': settings.postgres_port
    }
    with conn_context_es(settings.elastic_host, settings.elastic_port) as es_conn, \
            conn_context_postgres(dsl) as pg_conn:
        while True:
            postgres_to_es(es_conn, pg_conn)
            sleep(10)