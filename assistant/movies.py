from typing import Optional

import phrases
from api.models import Film
from api.search import SearchConnector
from phrases import get_phrase
from core.config import settings

api = SearchConnector(settings.SEARCHING_SERVICE)


def get_director(form, current_state):
    """Ищет режиссера по названию фильма."""
    api_req = {
        "film": form["slots"].get("film", {}).get("value"),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    current_state.update(api_req)

    if "film" not in current_state:
        return "Извините, не понимаю, что вы хотите", current_state

    film_name, directors_names = api.find_film_directors(current_state["film"])
    if not film_name:
        return "Я не смогла найти этот фильм", current_state

    if not directors_names:
        return (
            "Я не нашла режиссера фильма " + film_name,
            current_state,
        )

    return (
        get_phrase(phrases.DIRECTOR, film=film_name, director=directors_names),
        current_state,
    )


def get_film(form, current_state) -> Optional[Film]:
    """Ищет фильм по названию и рассказывает о нем информацию."""
    api_req = {
        "film": form["slots"].get("film", {}).get("value"),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    current_state.update(api_req)

    if "film" not in current_state:
        return "Извините, не понимаю, что вы хотите", current_state

    film = api._find_film_data(current_state["film"])
    if not film:
        return "Я не смогла найти этот фильм", current_state

    return (
        get_phrase(
            phrases.FILM_DESCRIPTION,
            film=film.title,
            genre=", ".join(film.genre) if film.genre else "",
            description=film.description,
            rating=film.imdb_rating,
        ),
        current_state,
    )


def get_actor(form, current_state):
    """Ищет актеров по названию фильма."""
    api_req = {
        "film": form["slots"].get("film", {}).get("value"),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    current_state.update(api_req)

    if "film" not in current_state:
        return "Извините, не понимаю, что вы хотите", current_state

    film_name, actors_names = api.find_film_actors(current_state["film"])
    if not film_name:
        return "Я не смогла найти этот фильм", current_state

    if not actors_names:
        return (
            "Я не нашла актеров фильма " + film_name,
            current_state,
        )

    return (
        get_phrase(phrases.ACTORS, film=film_name, actors=actors_names),
        current_state,
    )


def get_films(form, current_state):
    """Ищет топ фильмов, фильмы по жанрам."""
    is_next = form["slots"].get("next", {}).get("value")

    if is_next:
        if "page" not in current_state:
            return (
                "Извините, не понимаю, что вы хотите",
                current_state,
            )
        current_state["page"] += 1
    else:
        api_req = {
            "genre": form["slots"].get("genre", {}).get("value"),
        }
        current_state.update({**api_req, "page": 1})
    genre = current_state.get("genre")
    if genre:
        films = api.find_top_films(
            genre=genre, page=current_state["page"]
        )
    else:
        films = api.find_top_films(page=current_state["page"])

    if not films:
        return "Я не смогла найти ни одного фильма", current_state

    film_names = ". ".join(
        [film.title + ", рейтинг " + str(film.imdb_rating) for film in films]
    )

    return (
        get_phrase(phrases.FILMS, film=film_names)
        if current_state["page"] == 1
        else film_names,
        current_state,
    )


def get_person(form, current_state):
    """Ищет персону и его фильмы."""
    api_req = {
        "person": form["slots"].get("person", {}).get("value"),
    }
    api_req = {k: v for k, v in api_req.items() if v}
    current_state.update(api_req)

    if "person" not in current_state:
        return "Извините, не понимаю, что вы хотите", current_state

    person_name, film_names = api.find_person_films(current_state["person"])

    if not person_name:
        return "Я не смогла найти никого с таким именем", current_state

    if not film_names:
        return (
            "Я не нашла фильмов с участием " + person_name,
            current_state,
        )

    return (
        get_phrase(phrases.PERSON, person=person_name, film=film_names),
        current_state,
    )
