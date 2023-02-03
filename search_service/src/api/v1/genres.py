import logging
from http import HTTPStatus
from logging import config as logging_config
from typing import Optional

from src.core.logger import LOGGING
from fastapi import APIRouter, Depends, HTTPException
from src.models.data_models import Genre
from src.services.genre import GenreService, get_genre_service

from .params import PaginatedParams

GENRE_NOT_FOUND_STR = 'genres not found'

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')

router = APIRouter()


@router.get('/{genre_id}',
            response_model=Genre,
            description='Вывод одного жанра по id')
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=GENRE_NOT_FOUND_STR)
    return Genre(id=genre.id,
                 name=genre.name,
                 description=genre.description)


@router.get("/",
            description='Вывод всех жанров с учетом фильтров и сортировки')
async def get_all_genres(pagination: PaginatedParams = Depends(PaginatedParams),
                         sort="",
                         filter_name="",
                         filter_arg="",
                         genre_service: GenreService = Depends(get_genre_service)
                         ) -> Optional[list[Genre]]:
    logger.debug('Open api with all genres')

    genres = await genre_service.get_all_genres(page_size=pagination.page_size,
                                                page_number=pagination.page_number,
                                                sort=sort,
                                                filter_name=filter_name,
                                                filter_arg=filter_arg)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=GENRE_NOT_FOUND_STR)

    return genres


@router.get("/search/",
            description='Поиск жанров по запросу')
async def get_search_genres(
                            query: str,
                            genre_service: GenreService = Depends(get_genre_service),
                            pagination: PaginatedParams = Depends(PaginatedParams)
                            ) -> Optional[list[Genre]]:
    genres = await genre_service.get_search_genres(page_size=pagination.page_size,
                                                   page_number=pagination.page_number,
                                                   query=query)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=GENRE_NOT_FOUND_STR)

    return genres
