import json

import aiohttp
import pytest
from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(client_session: aiohttp.ClientSession):
    async def inner(endpoint: str, query_data: dict):
        url = test_settings.service_url + endpoint
        async with client_session.get(url, allow_redirects=False,timeout=1, params=query_data) as response:
            return response.status, await response.json()
    return inner