import os
from logging import config as logging_config

from src.core.logger import LOGGING

from pydantic import BaseSettings


class Settings(BaseSettings):
    logging_config.dictConfig(LOGGING)
    PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')
    REDIS_HOST = os.getenv('BROKER_HOST', '127.0.0.1')
    REDIS_PORT = int(os.getenv('BROKER_PORT', 6379))
    ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
    ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_page_size = 10
    default_page_number = 1
    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    class Config:
        env_file = '.env'


settings = Settings()
