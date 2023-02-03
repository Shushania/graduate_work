import json
from typing import List

import asyncpg
import pytest

from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def pg_client():
    con = await asyncpg.connect(
        host=test_settings.pg_host,
        port=test_settings.pg_port,
        database=test_settings.pg_name,
        user=test_settings.pg_user,
        password=test_settings.pg_password
    )
    yield con
    await con.close()


@pytest.fixture
def pg_write_data(pg_client):
    async def inner(data: List[tuple], table:str, columns:list):
        try:
            await pg_client.copy_records_to_table(
                table,
                records=data,
                columns=columns
            )
        except Exception as e:
            raise Exception(e)
    return inner