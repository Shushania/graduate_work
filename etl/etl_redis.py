from datetime import datetime

from decorator import backoff
from settings import Settings

from redis import Redis


class ETLRedis:
    def __init__(self):
        cnf = Settings()
        self.redis = Redis(
            host=cnf.broker_host,
            port=cnf.broker_port,
            decode_responses=True,
        )

    @backoff()
    def set_lasttime(self, key: str, lasttime: datetime):
        """
        Сохранение последнего datetime получения данных из PostgreSQL
        """
        key = f':lasttime_{key}'
        self.redis.set(key, lasttime.isoformat())

    @backoff()
    def get_lasttime(self, key: str) -> datetime:
        """
        Получение последнего datetime получения данных из PostgreSQL
        """
        key = f':lasttime_{key}'
        if self.redis.get(key) is None:
            return datetime(1970, 1, 1)
        return datetime.fromisoformat(self.redis.get(key))
