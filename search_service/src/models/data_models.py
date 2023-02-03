import uuid
from typing import Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """
    Декодирование, потому что orjson.dumps возвращает bytes,
    а pydantic требует unicode.
    """
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    """
    Базовый класс для API
    """

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class ListCache(BaseModel):
    __root__: list[str]


class Film(Base):
    id: uuid.UUID
    title: str
    description: Optional[str]


class GenreForFilm(Base):
    name: str


class PersonForFilm(Base):
    id: uuid.UUID
    name: str


class FilmForPerson(Base):
    id: uuid.UUID
    title: str
    rating: Optional[float]
    type: str


class Person(Base):
    id: uuid.UUID
    full_name: str


class Genre(Base):
    id: uuid.UUID
    name: str
    description: Optional[str]


class ElasticFilmWork(Base):
    id: uuid.UUID
    imdb_rating: float
    genre: Optional[list[str]]
    title: str
    description: Optional[str]
    director: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: Optional[list[PersonForFilm]]
    writers: Optional[list[PersonForFilm]]
