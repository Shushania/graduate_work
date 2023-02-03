import logging
from functools import lru_cache
from logging import config as logging_config
from typing import List, Optional

from fastapi import Depends

from src.core.logger import LOGGING
from src.db.redis import get_redis, AsyncCacheStorage
from src.models.data_models import Genre
from src.services.cache_generate import CacheObj, CacheKey
from src.db.elastic import get_elastic, AsyncDataProvider
from src.models.data_models import ListCache

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')


class GenreService(CacheKey):
    def __init__(self, redis: AsyncCacheStorage, elastic: AsyncDataProvider):
        self.redis = redis
        self.elastic = elastic
        self.index = 'genres'

    async def get_genre_by_id(self, genre_id: str):
        """
        Получаем информацию по одному genre,
         проверяя сначала кеш, потом эластику.
        """
        genre = await self.redis.get(key=genre_id)
        if not genre:
            genre_data = await self.elastic.get_by_id(
                index=self.index,
                id=genre_id
            )
            genre = Genre(**genre_data)
            if not genre:
                return None
            await self.redis.set(key=genre_id,
                                 value=genre.json())
            return genre
        genre_from_cache = Genre.parse_raw(genre)
        return genre_from_cache

    async def get_all_genres(
            self,
            page_size: int,
            page_number: int,
            sort: Optional[str],
            filter_name: Optional[str],
            filter_arg: Optional[str]
    ) -> Optional[List[Genre]]:
        """
        Получаем информацию по нескольким Genres,
         проверяя сначала кеш, потом эластику.
         Также учитываем фильтрацию и сортировку.
        """

        key = self._create_cache_key(
            [
                CacheObj(key_name='filter', key_value=f'{filter_name}_{filter_arg}'),
                CacheObj(key_name='sort', key_value=str(sort)),
                CacheObj(key_name='pagination', key_value=f'{page_size}_{page_number}')
            ]
        )

        genres = await self.redis.get(key)

        if not genres:
            genres_response = await self.elastic.get_all(
                index=self.index,
                sort=sort,
                filter_name=filter_name,
                filter_arg=filter_arg,
                page_number=page_number,
                page_size=page_size
            )
            genres = [Genre(**d) for d in genres_response]
            genres_data = ListCache.parse_obj([f.json() for f in genres]).json()
            if not genres:
                return None
            await self.redis.set(key=key, value=genres_data)
            return genres
        genres_data = ListCache.parse_raw(genres)
        genres_from_cache = [
            Genre.parse_raw(genre_data) for genre_data in genres_data.__root__
        ]
        return genres_from_cache

    async def get_search_genres(
            self,
            page_size: int,
            page_number: int,
            query: str
    ) -> Optional[List[Genre]]:
        """
        Поиск по Genres,
         проверяя сначала кеш, потом эластику.
        """

        key = self._create_cache_key(
            [
                CacheObj(key_name='query', key_value=str(query)),
                CacheObj(key_name='pagination', key_value=f'{page_size}_{page_number}')
            ]
        )
        genres = await self.redis.get(key)

        if not genres:
            genres_response = await self.elastic.search(
                index=self.index,
                query=query,
                page_number=page_number,
                page_size=page_size
            )
            genres = [Genre(**d) for d in genres_response]
            genres_data = ListCache.parse_obj([f.json() for f in genres]).json()
            if not genres:
                return None
            await self.redis.set(key=key, value=genres_data)
            return genres
        genres_data = ListCache.parse_raw(genres)
        genres_from_cache = [
            Genre.parse_raw(genre_data) for genre_data in genres_data.__root__
        ]
        return genres_from_cache


@lru_cache()
def get_genre_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: AsyncDataProvider = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
