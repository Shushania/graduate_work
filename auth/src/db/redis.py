from redis import StrictRedis

from config.config import settings

redis_db = StrictRedis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,
)
