import logging

import aioredis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from src.api.v1 import films, genres, persons
from src.core.config import settings
from src.db import elastic, redis
from src.middlewares.auth import AuthMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('root')

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

@app.on_event('startup')
async def startup():
    redis_client = await aioredis.create_redis_pool(
        (settings.REDIS_HOST, settings.REDIS_PORT),
        minsize=10, maxsize=20
    )
    redis.redis = redis.RedisCacheProvider(redis_client)
    elastic_client = AsyncElasticsearch(
        hosts=[f"{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}"]
    )
    elastic.es = elastic.AsyncElasticProvider(elastic_client)


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


app.add_middleware(BaseHTTPMiddleware, dispatch=AuthMiddleware())

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8060)
