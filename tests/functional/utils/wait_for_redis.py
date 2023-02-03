import logging
from redis import Redis

from tests.functional.decorator import backoff
from tests.functional.settings import test_settings


@backoff(logger=logging.getLogger('wait_for_redis::redis_conn'))
def redis_conn():
    Redis(
        host=test_settings.redis_host,
        port=test_settings.reids_port,
        decode_responses=True,
    )


if __name__ == '__main__':
    redis_conn()
