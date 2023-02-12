import random
from string import Template
from typing import List

INTRO = (
    'Привет! Какой фильм тебя интересует? '
)
HELP = (
    "Я умею отвечать на различные вопросы про фильмы."
    "Спроси меня: кто снимается в фильме, о чем фильм, кто снял фильм."
)
UNSUCCESSFUL = [
    "Извините, я вас не поняла"
]
NOTHING = [
    "Я не получила ваше сообщение, повторите пожалуйста"
]

EXIT = (
    "До скорых встреч!"
)

DIRECTOR = ["$director снял $film",
            "$film был снят $director ",
            ]

ACTORS = "В фильме $film снимались $actors"


FILM_DESCRIPTION = "$film. В жанрах $genre. Описание фильма следующее: $description. Рейтинг $rating."

PERSON = "$person снимался в  $film."

FILMS = [
    "Могу порекомендовать $film.",
    "Советую посмотреть $film.",
]


def get_phrase(phrase, **kwargs):
    template_string = random.choice(phrase) if isinstance(phrase, List) else phrase
    result = Template(template_string).substitute(**kwargs)
    return result
