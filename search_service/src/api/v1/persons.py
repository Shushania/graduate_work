import logging
from http import HTTPStatus
from logging import config as logging_config
from typing import Optional

from src.core.logger import LOGGING
from fastapi import APIRouter, Depends, HTTPException
from src.models.data_models import Person
from src.services.person import PersonService, get_person_service

from .params import PaginatedParams

PERSON_NOT_FOUND_STR = 'persons not found'

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')

router = APIRouter()


@router.get('/{person_id}',
            response_model=Person,
            description='Вывод персоны по id')
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=PERSON_NOT_FOUND_STR)
    return Person(id=person.id, full_name=person.full_name)


@router.get("/",
            description='Вывод всех персон учитывая фильтры и сортировку')
async def get_all_persons(pagination: PaginatedParams = Depends(PaginatedParams),
                          sort="",
                          filter_name="",
                          filter_arg="",
                          person_service: PersonService = Depends(get_person_service)
                          ) -> Optional[list[Person]]:
    logger.debug('Open api with all persons')

    persons = await person_service.get_all_persons(page_size=pagination.page_size,
                                                   page_number=pagination.page_number,
                                                   sort=sort,
                                                   filter_name=filter_name,
                                                   filter_arg=filter_arg)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=PERSON_NOT_FOUND_STR)

    return persons


@router.get("/search/",
            description='Поиск персон по запросу')
async def get_search_persons(
                            query: str,
                            person_service: PersonService = Depends(get_person_service),
                            pagination: PaginatedParams = Depends(PaginatedParams)
                           ) -> Optional[list[Person]]:
    persons = await person_service.get_search_persons(page_size=pagination.page_size,
                                                      page_number=pagination.page_number,
                                                      query=query)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=PERSON_NOT_FOUND_STR)

    return persons
