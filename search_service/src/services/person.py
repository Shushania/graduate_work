import logging
from functools import lru_cache
from logging import config as logging_config
from typing import List, Optional

from fastapi import Depends

from src.core.logger import LOGGING
from src.db.elastic import get_elastic, AsyncDataProvider
from src.db.redis import get_redis, AsyncCacheStorage
from src.models.data_models import Person
from src.services.cache_generate import CacheKey, CacheObj
from src.models.data_models import ListCache

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')


class PersonService(CacheKey):
    def __init__(self,
                 redis: AsyncCacheStorage,
                 elastic: AsyncDataProvider):
        self.redis = redis
        self.elastic = elastic
        self.index = 'persons'

    async def get_person_by_id(self, person_id: str):
        """
        Получаем информацию по одному person,
         проверяя сначала кеш, потом эластику.
        """
        person = await self.redis.get(key=person_id)

        if not person:
            person_data = await self.elastic.get_by_id(
                index=self.index,
                id=person_id
            )
            person = Person(**person_data)
            if not person:
                return None
            await self.redis.set(key=person_id,
                                 value=person.json())
            return person
        person_from_cache = Person.parse_raw(person)
        return person_from_cache

    async def get_all_persons(
            self,
            page_size: int,
            page_number: int,
            sort: Optional[str],
            filter_name: Optional[str],
            filter_arg: Optional[str],
    ) -> Optional[List[Person]]:
        """
        Получаем информацию по нескольким Persons,
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

        persons = await self.redis.get(key)

        if not persons:
            persons_response = await self.elastic.get_all(
                index=self.index,
                sort=sort,
                filter_name=filter_name,
                filter_arg=filter_arg,
                page_number=page_number,
                page_size=page_size
            )
            persons = [Person(**d) for d in persons_response]
            persons_data = ListCache.parse_obj([f.json() for f in persons]).json()
            if not persons:
                return None
            await self.redis.set(key=key, value=persons_data)
            return persons
        persons_data = ListCache.parse_raw(persons)
        persons_from_cache = [
            Person.parse_raw(person_data) for person_data in persons_data.__root__
        ]
        return persons_from_cache

    async def get_search_persons(
            self,
            page_size: int,
            page_number: int,
            query: str
    ) -> Optional[List[Person]]:
        """
        Поиск по Persons,
         проверяя сначала кеш, потом эластику.
        """
        key = self._create_cache_key(
            [
                CacheObj(key_name='query', key_value=str(query)),
                CacheObj(key_name='pagination', key_value=f'{page_size}_{page_number}')
            ]
        )

        persons = await self.redis.get(key)

        if not persons:
            persons_response = await self.elastic.search(
                index=self.index,
                query=query,
                page_number=page_number,
                page_size=page_size
            )
            persons = [Person(**d) for d in persons_response]
            persons_data = ListCache.parse_obj([f.json() for f in persons]).json()
            if not persons:
                return None
            await self.redis.set(key=key, value=persons_data)
            return persons
        persons_data = ListCache.parse_raw(persons)
        persons_from_cache = [
            Person.parse_raw(person_data) for person_data in persons_data.__root__
        ]
        return persons_from_cache


@lru_cache()
def get_person_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: AsyncDataProvider = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
