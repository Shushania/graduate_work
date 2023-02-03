from http import HTTPStatus
import pytest

from tests.functional.testdata.es_mapping import genres
from tests.functional.testdata.validate_mapping import genre_map
from tests.functional.utils.helpers import get_all_cache_key, set_uuid


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест для получение конкретного жанра
        (
                {
                   'all': False
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 3
                }
        ),
        # Тест для получение всех жанров
        (
                {
                    'all': True,
                    'page_number': 1
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 10
                }
        )
    ]
)
@pytest.mark.asyncio
async def test_genres(query_data, expected_answer, es_write_data, make_get_request, get_from_cache):
    es_data = await set_uuid(genres)

    await es_write_data(es_data, 'genre')

    if query_data.pop('all'):
        """
        Вывод всех фильмов
        """
        status, body = await make_get_request('/api/v1/genres/', query_data)
        """
        Валидация фильмов
        """
        for item in body:
            if type(item) == dict:
                assert list(item.keys()) == genre_map

        key = await get_all_cache_key(
            'genres',
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
        status, body = await make_get_request(f'/api/v1/genres/{str(es_data[0]["id"])}', query_data)

        key = es_data[0]["id"]

        """
        Валидация конкретного фильма
        """
        assert list(body.keys()) == genre_map

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
