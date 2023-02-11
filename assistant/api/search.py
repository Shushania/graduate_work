from http import HTTPStatus
from typing import List, Optional, Tuple
from uuid import UUID

import requests

from .models import Film, FilmBase, Person


class SearchConnector:
    def __init__(self, url):
        self._url = url

    def _get_response(self, path: str, query: str = ""):
        response = requests.get(self._url + path, params=query)
        return response

    def find_film_directors(self, query: str):
        film = self._find_film_data(query)
        if not film:
            return None, None
        return film.title, ", ".join(film.director)

    def find_film_actors(self, query: str, limit: int = 5):
        film = self._find_film_data(query)
        if not film:
            return None, None
        return film.title, ", ".join(film.actors_names[:limit])

    def find_top_films(self, genre: str = None, page: int = 1):
        films = self._find_films(genre=genre, page=page)
        return films

    def find_person_films(self, query: str):
        person = self._find_person(query)
        if not person:
            return None, None

        films = self._get_films_by_person_uuid(person.id)
        film_names = ", ".join(film.title for film in films) if films else None

        return person.full_name, film_names

    def _find_film_data(self, query: str) -> Optional[UUID]:
        response = self._get_response(
            "films/",
            query={
                "sort": "imdb_rating",
                "filter_name": "title",
                "filter_arg": query,
            },
        )
        if response.status_code != HTTPStatus.OK:
            return None

        return Film(**response.json()["values"][0])

    def _get_film_by_uuid(self, film_uuid: UUID) -> Optional[Film]:
        response = self._get_response(f"films/{film_uuid}")
        if response.status_code != HTTPStatus.OK:
            return None

        return Film(**response.json())

    def _find_films(self, genre: str = None, page: int = 1, size: int = 3):
        if genre:
            response = self._get_response(
                "films/",
                query={
                    "sort": "imdb_rating",
                    "filter_name": "genre",
                    "filter_arg": genre,
                    "page_number": page,
                    "page_size": size,
                },
            )
        else:
            response = self._get_response(
                "films/",
                query={
                    "sort": "imdb_rating",
                    "page_number": page,
                    "page_size": size,
                },
            )

        if response.status_code != HTTPStatus.OK:
            return None
        return [FilmBase(**row) for row in response.json()["values"]]

    def _find_person(self, query: str) -> Optional[Person]:
        response = self._get_response(
            "persons/search/",
            query={
                "query": query,
            },
        )
        if response.status_code != HTTPStatus.OK:
            return None
        return Person(**response.json()["values"][0])

    def _get_films_by_person_uuid(self, person_uuid: UUID) -> Optional[List[Film]]:
        response = self._get_response(f"persons/{person_uuid}")
        if response.status_code != HTTPStatus.OK:
            return None

        film_ids = response.json()["film_ids"][:5]
        films = []

        for film_id in film_ids:
            film = self._get_film_by_uuid(film_id)
            if film:
                films.append(film)

        return films
