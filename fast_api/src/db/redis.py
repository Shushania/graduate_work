from abc import ABC, abstractmethod
from typing import Optional

from aioredis import Redis

from src.core.config import settings


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, **kwargs):
        pass


class RedisCacheProvider(AsyncCacheStorage):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[dict]:
        data = await self.redis_client.get(key=key)
        if not data:
            return None
        return data

    async def set(self, key: str, value: str):
        await self.redis_client.set(key=key,
                                    value=value,
                                    expire=settings.FILM_CACHE_EXPIRE_IN_SECONDS)


redis: Optional[AsyncCacheStorage] = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis
