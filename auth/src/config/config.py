import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    redis_host: str = os.getenv('REDIS_HOST', 'redis')
    redis_port: int = int(os.getenv('redis_port', 6379))
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    postgres_name: str = os.getenv('POSTGRES_DB', 'movies_db')
    postgres_user: str = os.getenv('POSTGRES_USER', 'app')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD', '123qwe')
    postgres_host: str = os.getenv('POSTGRES_HOST', 'pg')
    postgres_port: int = os.getenv('POSTGRES_PORT', 5432)
    enable_tracer: bool = os.getenv('ENABLE_TRACER', True)

    oauth_credentials = {
        'yandex': {
            'id': os.getenv("YANDEX_ID"),
            'secret': os.getenv("YANDEX_SECRET"),
            'get_callback_url': os.getenv("YANDEX_CALLBACK"),
            'authorize_url': 'https://oauth.yandex.ru/authorize',
            'access_token_url': 'https://oauth.yandex.ru/token',
            'base_url': 'https://login.yandex.ru/',
        },
        'google': {
            'id': os.getenv("GOOGLE_ID"),
            'secret': os.getenv("GOOGLE_SECRET"),
            'get_callback_url': os.getenv("GOOGLE_CALLBACK"),
            'authorize_url': 'https://accounts.google.com/',
            'access_token_url': 'https://oauth2.googleapis.com/token',
            'base_url': 'https://www.googleapis.com/oauth2/v1/'
        },
    }

    class Config:
        env_file = '.env'
        env_prefix = 'AUTH_'
        env_nested_delimiter = '_'


class HTTPStatus(BaseSettings):
    created: str = os.getenv('CREATED', 'New one was registered successfully')
    conflict: str = os.getenv('CONFLICT', 'The username already exists')
    not_found: str = os.getenv('NOT_FOUND', 'User is not found')
    bad_request: str = os.getenv('BAD_REQUEST', 'Wrong password')
    withdrawn: str = os.getenv('WITHDRAWN', 'Token withdrawn successfully')
    changed: str = os.getenv('CHANGED', 'Login/password/role changed')
    required: str = os.getenv('REQUIRED', 'Required login or password')
    not_found_role: str = os.getenv('NOT_FOUND_ROLE', "Role with this id doesn't exists")
    link_role: str = os.getenv('LINK_ROLE', 'Role link to user successfully')
    unlink_role: str = os.getenv('UNLINK_ROLE', 'Role unlink to user successfully')

    class Config:
        env_file = '.http_status'
        env_prefix = 'AUTH_'
        env_nested_delimiter = '_'


statuses = HTTPStatus()
settings = Settings()
