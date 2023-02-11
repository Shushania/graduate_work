import uuid
from typing import List, Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: uuid.UUID
    full_name: str


class PersonForFilm(BaseModel):
    id: uuid.UUID
    name: str


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class FilmBase(BaseModel):
    """Фильм в списке."""

    id: uuid.UUID
    title: str
    imdb_rating: float


class Film(FilmBase, BaseModel):
    """Подробная информация о фильме."""

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
