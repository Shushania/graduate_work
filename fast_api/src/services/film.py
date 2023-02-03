import logging
from functools import lru_cache
from logging import config as logging_config
from typing import List, Optional

from fastapi import Depends

from src.core.logger import LOGGING
from src.db.redis import get_redis, AsyncCacheStorage
from src.models.data_models import ElasticFilmWork, Film
from src.services.cache_generate import CacheKey, CacheObj
from src.db.elastic import get_elastic, AsyncDataProvider
from src.models.data_models import ListCache

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')


class FilmService(CacheKey):
    def __init__(self, redis: AsyncCacheStorage, elastic: AsyncDataProvider):
        self.redis = redis
        self.elastic = elastic
        self.index = 'movies'

    async def get_film_by_id(self, film_id: str):
        """
        Получаем информацию по одному фильму,
         проверяя сначала кеш, потом эластику.
        """
        film = await self.redis.get(key=film_id)
        if not film:
            film_data = await self.elastic.get_by_id(
                index=self.index,
                id=film_id)
            film = Film(**film_data)
            if not film:
                return None
            await self.redis.set(key=film_id,
                                 value=film.json())
            return film
        film_from_cache = Film.parse_raw(film)
        return film_from_cache

    async def get_all_films(
            self,
            page_size: int,
            page_number: int,
            sort: Optional[str],
            filter_name: Optional[str],
            filter_arg: Optional[str]
    ) -> Optional[List[ElasticFilmWork]]:
        """
        Получаем информацию по нескольким фильмам,
         проверяя сначала кеш, потом эластику.
         Также учитываем фильтрацию и сортировку.
        """

        key = self._create_cache_key(
            [
                CacheObj(key_name='filter', key_value=f'{filter_name}_{filter_arg}'),
                CacheObj(key_name='sort', key_value=str(sort))
            ]
        )

        films = await self.redis.get(key=key)
        if not films:
            films_response = await self.elastic.get_all(
                index=self.index,
                sort=sort,
                filter_name=filter_name,
                filter_arg=filter_arg,
                page_number=page_number,
                page_size=page_size
            )
            films = [ElasticFilmWork(**d) for d in films_response]
            films_data = ListCache.parse_obj([f.json() for f in films]).json()
            if not films:
                return None
            await self.redis.set(key=key, value=films_data)
            return films
        films_data = ListCache.parse_raw(films)
        film_from_cache = [
            ElasticFilmWork.parse_raw(film_data) for film_data in films_data.__root__
        ]
        return film_from_cache

    async def get_search_films(
            self,
            page_size: int,
            page_number: int,
            query: str
    ) -> Optional[List[ElasticFilmWork]]:
        """
        Поиск по всем фильмам,
             проверяя сначала кеш, потом эластику.

        """

        key = self._create_cache_key(
            [
                CacheObj(key_name='query', key_value=str(query))
            ]
        )

        films = await self.redis.get(key=key)
        if not films:
            films_response = await self.elastic.search(
                index=self.index,
                query=query,
                page_number=page_number,
                page_size=page_size
            )
            films = [ElasticFilmWork(**d) for d in films_response]
            films_data = ListCache.parse_obj([f.json() for f in films]).json()
            if not films:
                return None
            await self.redis.set(key=key, value=films_data)
            return films
        films_data = ListCache.parse_raw(films)
        film_from_cache = [
            ElasticFilmWork.parse_raw(film_data) for film_data in films_data.__root__
        ]
        return film_from_cache


@lru_cache()
def get_film_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: AsyncDataProvider = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
