from http import HTTPStatus
from uuid import UUID

import httpx

from .models import Film, FilmBase, Person


class SearchConnector:
    def __init__(self, url):
        self._url = url

    def _get_response(self, path: str, query: str = ""):
        response = httpx.get(self._url + path, params=query)
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
        films = self._get_films_by_actors(query)
        return person.full_name, films

    def _find_film_data(self, query: str):
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

    def _get_film_by_uuid(self, film_uuid: UUID):
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
                    "page[number]": page,
                    "page[size]": size,
                },
            )
        else:
            response = self._get_response(
                "films/",
                query={
                    "sort": "imdb_rating",
                    "page[number]": page,
                    "page[size]": size,
                },
            )

        if response.status_code != HTTPStatus.OK:
            return None
        return [FilmBase(**row) for row in response.json()["values"]]

    def _find_person(self, query: str):
        response = self._get_response(
            "persons/search/",
            query={
                "query": query,
            },
        )
        if response.status_code != HTTPStatus.OK:
            return None
        return Person(**response.json()["values"][0])

    def _get_films_by_actors(self, query):
        response = self._get_response(
            "films/",
            query={
                "sort": "imdb_rating",
                "filter_name": "actors_names",
                "filter_arg": query,
            },
        )
        if response.status_code != HTTPStatus.OK:
            return None
        films = ', '.join([film["title"] for film in response.json()["values"]])

        return films
