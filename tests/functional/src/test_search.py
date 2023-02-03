from http import HTTPStatus
import pytest

from tests.functional.testdata.es_mapping import films, genres, persons
from tests.functional.testdata.validate_mapping import all_film_map, genre_map, person_map
from tests.functional.utils.helpers import get_all_cache_key, set_uuid


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест для поиска фильмов
        (
                {
                    'query': 'The Star',
                    'page_number': 1,
                    'not_found': False
                 },
                {
                    'status': HTTPStatus.OK,
                    'length': 10
                }
        ),
        # Тест для некорректного поиска фильмов
        (
                {
                    'query': 'Mashed potato',
                    'page_number': 1,
                    'not_found': True
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'length': 1
                }
        )
    ]
)
@pytest.mark.asyncio
async def test_film_search(query_data, expected_answer, es_write_data, make_get_request, get_from_cache):
    """
    Тесты для поиска фильмов
    """
    not_found = query_data.pop('not_found')
    es_data = await set_uuid(films)
    await es_write_data(es_data, 'film')

    """
    Вывод всех фильмов
    """

    status, body = await make_get_request('/api/v1/films/search/', query_data)

    """
    Валидация фильмов
    """

    for item in body:
        if type(item) == dict:
            assert list(item.keys()) == all_film_map
    key = await get_all_cache_key(
        'movies',
        [
            {
                'key_name': 'query',
                'key_value': f'{query_data.get("query", "")}'
            }
        ]
    )

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка кол-ва полученных данных
    """

    assert len(body) == expected_answer["length"]

    """
    Проверка кэша
    """

    if not_found:
        body = None
    assert body == await get_from_cache(key)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест для поиска жанров
        (
                {
                    'query': 'Action',
                    'page_number': 1,
                    'not_found': False
                 },
                {
                    'status': HTTPStatus.OK,
                    'length': 10
                }
        ),
        # Тест для некорректного поиска жанров
        (
                {
                    'query': 'Drama',
                    'page_number': 1,
                    'not_found': True
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'length': 1
                }
        )
    ]
)
@pytest.mark.asyncio
async def test_genre_search(query_data, expected_answer, es_write_data, make_get_request, get_from_cache):
    """
    Тесты для поиска жанров
    """
    not_found = query_data.pop('not_found')
    es_data = await set_uuid(genres)
    await es_write_data(es_data, 'genre')

    """
    Вывод всех жанров
    """

    status, body = await make_get_request('/api/v1/genres/search/', query_data)

    """
    Валидация жанров
    """

    for item in body:
        if type(item) == dict:
            assert list(item.keys()) == genre_map
    key = await get_all_cache_key(
        'genres',
        [
            {
                'key_name': 'query',
                'key_value': f'{query_data.get("query", "")}'
            }
        ]
    )

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка кол-ва полученных данных
    """

    assert len(body) == expected_answer["length"]

    """
    Проверка кэша
    """
    if not_found:
        body = None
    assert body == await get_from_cache(key)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест для поиска персон
        (
                {
                    'query': 'Johnny Depp',
                    'page_number': 1,
                    'not_found': False
                 },
                {
                    'status': HTTPStatus.OK,
                    'length': 10
                }
        ),
        # Тест для некорректного поиска персон
        (
                {
                    'query': 'George',
                    'page_number': 1,
                    'not_found': True
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'length': 1
                }
        )
    ]
)
@pytest.mark.asyncio
async def test_person_search(query_data, expected_answer, es_write_data, make_get_request, get_from_cache):
    """
    Тесты для поиска персон
    """
    not_found = query_data.pop('not_found')
    es_data = await set_uuid(persons)
    await es_write_data(es_data, 'person')

    """
    Вывод всех персон
    """

    status, body = await make_get_request('/api/v1/persons/search/', query_data)

    """
    Валидация персон
    """

    for item in body:
        if type(item) == dict:
            assert list(item.keys()) == person_map
    key = await get_all_cache_key(
        'persons',
        [
            {
                'key_name': 'query',
                'key_value': f'{query_data.get("query", "")}'
            }
        ]
    )

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка кол-ва полученных данных
    """

    assert len(body) == expected_answer["length"]

    """
    Проверка кэша
    """
    if not_found:
        body = None
    assert body == await get_from_cache(key)
