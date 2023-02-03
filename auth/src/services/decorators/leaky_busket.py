import datetime
import os

import redis
from flask_jwt_extended import get_jwt

REQUEST_LIMIT_PER_MINUTE = int(os.getenv('REQUEST_LIMIT_PER_MINUTE', 20))

redis_conn = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    db=os.getenv('REDIS_DB_RATE_LIMITS', 0))


def limit_leaky_bucket(func):
    def limit_leaky_bucket_wrapper(*args, **kwargs):
        jti = get_jwt()

        pipe = redis_conn.pipeline()
        now = datetime.datetime.now()
        key = f'{jti["sub"]}:{now.minute}'
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = pipe.execute()

        request_number = result[0]
        if request_number > REQUEST_LIMIT_PER_MINUTE:
            return {'message': f'Too many requests ({request_number})'}, 429
        else:
            return func(*args, **kwargs)

    limit_leaky_bucket_wrapper.__name__ = func.__name__
    return limit_leaky_bucket_wrapper