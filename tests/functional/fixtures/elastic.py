import json
from typing import List

import pytest
from elasticsearch import AsyncElasticsearch
from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=[f'{test_settings.es_host}:{test_settings.es_port}'],
        validate_cert=False,
        use_ssl=False
    )
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: List[dict], index:str):
        bulk_query = []
        for row in data:
            bulk_query.extend([
                json.dumps({'index': {'_index': test_settings.es_index.get(index), '_id': row['id']}}),
                json.dumps(row)
            ])

        str_query = '\n'.join(bulk_query) + '\n'

        response = await es_client.bulk(str_query, refresh=True)

        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner