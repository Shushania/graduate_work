import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Filmwork:
    title: str
    description: str
    type: str
    creation_date: datetime
    created_at: datetime = field(default_factory=datetime.now())
    updated_at: datetime = field(default_factory=datetime.now())
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre:
    name: str
    description: str
    created_at: datetime = field(default_factory=datetime.now())
    updated_at: datetime = field(default_factory=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    full_name: str
    created_at: datetime = field(default_factory=datetime.now())
    updated_at: datetime = field(default_factory=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmwork:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime = field(default_factory=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmwork:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime = field(default_factory=datetime.now())
    id: uuid.UUID = field(default_factory=uuid.uuid4)
