from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    pg_host: str = Field('pg', env='POSTGRES_HOST')
    pg_port: str = Field(5432, env='POSTGRES_PORT')
    pg_name: str = Field('movies_db', env='POSTGRES_DB')
    pg_user: str = Field('app', env='POSTGRES_USER')
    pg_password: str = Field('123qwe', env='POSTGRES_PASSWORD')
    service_url: str = Field('http://127.0.0.1', env='SERVICE_URL')

test_settings = TestSettings()