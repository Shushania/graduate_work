from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1', env='ELASTIC_HOST')
    es_port: str = Field('9200', env='ELASTIC_PORT')
    es_index: dict = Field({}, env='ELASTIC_INDEX')
    redis_host: str = Field('redis', env='BROKER_HOST')
    reids_port: str = Field('6379', env='BROKER_PORT')
    service_url: str = Field('http://127.0.0.1', env='SERVICE_URL')
    cache_separator: str = '::'

test_settings = TestSettings()