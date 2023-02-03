from elasticsearch import Elasticsearch
import logging

from tests.functional.decorator import backoff
from tests.functional.settings import test_settings


@backoff(logger=logging.getLogger('wait_for_es::es_conn'))
def es_conn():
    Elasticsearch(f"{test_settings.es_host}://{test_settings.es_host}:{test_settings.es_port}")


if __name__ == '__main__':
    es_conn()
