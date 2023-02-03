import logging

import psycopg2

from tests.functional.decorator import backoff
from tests.functional.settings import test_settings


@backoff(logger=logging.getLogger('wait_for_pg::pg_conn'))
def pg_conn():
    dsl = {
        'dbname': test_settings.pg_name,
        'user': test_settings.pg_user,
        'password': test_settings.pg_password,
        'host': test_settings.pg_host,
        'port': test_settings.pg_port
    }
    psycopg2.connect(**dsl)


if __name__ == '__main__':
    pg_conn()
