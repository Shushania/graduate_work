import uuid

from tests.functional.settings import test_settings

async def set_uuid(data: dict) -> dict:
    es_data = []
    for _ in range(20):
        data["id"]=str(uuid.uuid4())
        es_data.append(data.copy())
    return es_data


async def get_all_cache_key(index: str, values: list) -> str:
    key = f'{index}{test_settings.cache_separator}'
    for value in values:
        key += f'{value["key_name"]}{test_settings.cache_separator}{value["key_value"]},'
    return key
