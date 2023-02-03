import logging
from http import HTTPStatus
from logging import config as logging_config
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.core.logger import LOGGING
from src.models.data_models import ElasticFilmWork, Film
from src.services.film import FilmService, get_film_service

from .params import PaginatedParams

FILM_NOT_FOUN_STR = 'film not found'

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')

router = APIRouter()


@router.get('/{film_id}',
            response_model=Film,
            description='Вывод одного фильма по id')
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_film_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUN_STR)
    return Film(id=film.id,
                title=film.title,
                description=film.description)


@router.get("/",
            description='Вывод всех фильм учитывая сортировку и фильтр')
async def get_all_films(
        sort="",
        filter_name="",
        filter_arg="",
        film_service: FilmService = Depends(get_film_service),
        pagination: PaginatedParams = Depends(PaginatedParams)
) -> Optional[list[Film]]:
    films = await film_service.get_all_films(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        sort=sort,
        filter_name=filter_name,
        filter_arg=filter_arg)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUN_STR)

    return films


@router.get("/search/",
            description='Поиск фильмов по запросу')
async def get_search_films(
        query: str,
        film_service: FilmService = Depends(get_film_service),
        pagination: PaginatedParams = Depends(PaginatedParams)
) -> Optional[list[Film]]:
    films = await film_service.get_search_films(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        query=query)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=FILM_NOT_FOUN_STR)

    return films
