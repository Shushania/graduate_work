import random
from string import Template
from typing import List

INTRO = (
    'Привет! Какой фильм тебя интересует? '
)
HELP = (
    "Например, вы можете узнать информацию о фильме, "
    "искать популярное кино по жанрами, найти режиссера или актера любого фильма."
)
UNSUCCESSFUL = [
    "Хьюстон, у нас проблемы! Кажется я такое не умею.",
    "Я не поняла, спросите что-нибудь другое.",
]
EXIT = (
    "Приятно было поискать для вас! "
    'Чтобы вернуться в навык, скажите "Запусти навык Кинотеатр Практикума". До свидания!'
)

DIRECTOR = "$film снял $director"

ACTORS = [
    "В картине $film приняли участие $actors",
    "В фильме $film снимались $actors",
]

FILM_DESCRIPTION = "$film. $genre. $description. Рейтинг $rating."

PERSON = "Имя $person можно найти в титрах таких фильмов, как $film."

FILMS = [
    "Могу порекомендовать $film.",
    "Попробуйте посмотреть $film.",
    "Вам могут понравиться $film.",
]


def get_phrase(phrase, **kwargs):
    template_string = random.choice(phrase) if isinstance(phrase, List) else phrase
    result = Template(template_string).substitute(**kwargs)
    return result
