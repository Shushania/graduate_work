import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Filmwork:
    title: str
    description: str
    type: str
    actors: json
    writers: json
    genre: list
    director: list
    actors_names: list
    writers_names: list
    imdb_rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre:
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)