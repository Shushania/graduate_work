from http import HTTPStatus

import pytest
from tests.functional.testdata.es_mapping import films
from tests.functional.testdata.validate_mapping import all_film_map, film_map
from tests.functional.utils.helpers import get_all_cache_key, set_uuid


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест для получение конкретного фильма
        (
                {
                   'all': False
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 3
                }
        ),
        # Тест для получение всех фильмов без фильтрации
        (
                {
                    'all': True,
                    'page_number': 1
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 10
                }
        ),
        # Тест для получение всех фильмов с конретным актером
        (
                {
                    'all': True,
                    'page_number': 1,
                    'filter_name': 'actors_names',
                    'filter_arg': 'Johnny'
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 10
                }
        )
    ]
)
@pytest.mark.asyncio
async def test_films(query_data, expected_answer, es_write_data, make_get_request, get_from_cache):
    es_data = await set_uuid(films)

    await es_write_data(es_data, 'film')

    if query_data.pop('all'):
        if query_data.get('filter_name') is not None:
            """
            Поиск всех фильмов с участием актера
            """
            status, body = await make_get_request('/api/v1/films/', query_data)

        else:
            """
            Вывод всех фильмов
            """
            status, body = await make_get_request('/api/v1/films/', query_data)
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
                    'key_name': 'filter',
                    'key_value': f'{query_data.get("filter_name", "")}_{query_data.get("filter_arg", "")}'
                },
                {
                    'key_name': 'sort',
                    'key_value': f'{query_data.get("sort", "")}'
                }
            ]
        )
    else:
        """
        Вывод конкретного фильма
        """
        status, body = await make_get_request(f'/api/v1/films/{es_data[0]["id"]}', query_data)

        key = es_data[0]["id"]

        """
        Валидация конкретного фильма
        """
        assert list(body.keys()) == film_map

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

    assert body == await get_from_cache(key)
