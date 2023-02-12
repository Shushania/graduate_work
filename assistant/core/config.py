import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    SEARCHING_SERVICE = os.getenv('SEARCHING_SERVICE', 'http://51.250.96.235:8000/api/v1/')

    class Config:
        env_file = '.env.example'


settings = Settings()
