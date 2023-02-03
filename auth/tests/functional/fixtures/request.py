import json

import aiohttp
import pytest

from src.app import test
from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def flask_client():
    app_test = test()
    client = app_test.test_client()
    yield client


@pytest.fixture
def make_request(flask_client):
    async def inner(endpoint: str, query_data: dict, method: str):
        url = test_settings.service_url + endpoint
        headers = {
            "Host": "localhost",
            "X-Request-Id": "12345678",
            "Content-Type": "application/json"
        }
        if "auth" in query_data.keys():
            headers["Authorization"] = f"Bearer {query_data.pop('auth')}"
        if method == "GET":
            response = flask_client.get(url, query_string=query_data, headers=headers)
        elif method == "POST":
            response = flask_client.post(url, json=query_data, headers=headers)
        elif method == "PATCH":
            response = flask_client.patch(url, json=query_data, headers=headers)
        elif method == "DELETE":
            response = flask_client.delete(url, json=query_data, headers=headers)
        return response.status_code , response.get_json()
    return inner
