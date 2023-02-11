import ast

import pytest
from aioredis import Redis, create_redis_pool
from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def redis_client():
    redis = await create_redis_pool(
        (test_settings.redis_host, test_settings.reids_port),
        minsize=10, maxsize=20
    )
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture
def get_from_cache(redis_client: Redis):
    async def inner(key: str):
        data = await redis_client.get(key)
        if data is not None:
            data = ast.literal_eval(data.decode("utf-8"))
            if type(data) == list:
                for i in range(len(data)):
                    data[i] = ast.literal_eval(data[i])
        return data
    return inner
