from http import HTTPStatus

import pytest

from src.config.config import statuses
from tests.functional.testdata.pg_mapping import users
from tests.functional.testdata.validate_mapping import (login_map, refresh_map,
                                                        users_history_map)
from tests.functional.utils.helpers import (get_access_token,
                                            get_refresh_token, set_users)

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест регистрации
        (
                {
                    'login': 'user_signup_1',
                    'email': 'user_signup_1@mail.ru',
                    'password': '123'
                },
                {
                    'status': HTTPStatus.CREATED,
                    'message': statuses.created
                }
        ),
        # Тест регистрации с существующим логином
        (
                {
                    'login': 'user_signup_1',
                    'email': 'user_signup_1@mail.ru',
                    'password': False
                },
                {
                    'status': HTTPStatus.CONFLICT,
                    'message': statuses.conflict
                }
        ),
        # Тест регистрации с существующей почтой
        (
                {
                    'login': 'user_signup_2',
                    'email': 'user_signup_1@mail.ru',
                    'password': False
                },
                {
                    'status': HTTPStatus.CONFLICT,
                    'message': statuses.conflict
                }
        )
    ]
)
async def test_auth_signup(query_data, expected_answer, make_request):
    """
    Тесты для регистрации пользователя
    """

    """
    Отправление запроса
    """

    status, body = await make_request('/api/v1/auth/signup', query_data, "POST")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка сообщения запроса
    """

    assert body['message'] == expected_answer["message"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест авторизации с существующим пользователем и правильным паролем
        (
                {
                    'exists': True,
                    'correct_password': True,
                    'login': 'user_login_1',
                    'password': '123'
                },
                {
                    'status': HTTPStatus.OK
                }
        ),
        # Тест авторизации с существующим пользователем и неправильным паролем
        (
                {
                    'exists': True,
                    'correct_password': False,
                    'login': 'user_login_2',
                    'password': '123'
                },
                {
                    'status': HTTPStatus.BAD_REQUEST,
                    'message': statuses.bad_request
                }
        ),
        # Тест авторизации с несуществующим пользователем
        (
                {
                    'exists': False,
                    'correct_password': True,
                    'login': 'user_login_3',
                    'password': '123'
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': statuses.not_found
                }
        ),
    ]
)
async def test_auth_login(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для авторизации пользователя
    """

    if query_data.pop("exists"):
        """
        Занесение данных по пользователю в БД
        """

        pg_data = await set_users(data=users, login=[query_data["login"]], password=query_data["password"])
        await pg_write_data(data=pg_data, table='users', columns=list(users.keys()))

    if not query_data.pop("correct_password"):
        query_data["password"] = "incorrect"

    """
    Отправление запроса
    """

    status, body = await make_request('/api/v1/auth/login', query_data, "POST")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    if status == HTTPStatus.OK:
        """
        Валидация запроса
        """

        assert list(body.keys()) == login_map

    else:
        """
        Проверка сообщения запроса
        """

        assert body['message'] == expected_answer["message"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест логаута с существующим пользователем
        (
                {
                    'login': 'user_logout_1',
                    'password': '123'
                },
                {
                    'status': HTTPStatus.OK,
                    "message": statuses.withdrawn
                }
        ),
    ]
)
async def test_auth_logout(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для логаута пользователя
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(data=users, login=[query_data.pop("login")], password=query_data.pop("password"))
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()))

    """
    Получение access токена
    """

    access_tokens = await get_access_token(users=pg_data, is_superuser=False, roles=[])
    query_data["auth"] = access_tokens[0]

    """
    Отправление запроса
    """

    status, body = await make_request('/api/v1/auth/logout', query_data, "DELETE")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка сообщения запроса
    """

    assert body['message'] == expected_answer["message"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест ревреша access токена
        (
                {
                    'login': 'user_refresh_1',
                    'password': '123'
                },
                {
                    'status': HTTPStatus.OK
                }
        ),
    ]
)
async def test_auth_refresh(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для рефреша access токена
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(data=users, login=[query_data.pop("login")], password=query_data.pop("password"))
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()))

    """
    Получение refresh токена
    """

    refresh_tokens = await get_refresh_token(users=pg_data, is_superuser=False, roles=[])

    """
    Отправление запроса
    """

    query_data["auth"] = refresh_tokens[0]
    status, body = await make_request('/api/v1/auth/refresh', query_data, "POST")

    """
    Валидация ответа запроса
    """

    assert list(body.keys()) == refresh_map
    access_tokens = body['access_token']

    """
    Проверка нового access токена
    """

    query_data["auth"] = access_tokens
    status, body = await make_request('/api/v1/auth/history', query_data, "GET")
    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест изменения логина и пароля
        (
                {
                    'correct_password': True,
                    'login': 'user_change_1',
                    'old_password': '123',
                    'new_login': 'user_change_new_1',
                    'new_password': '1234'
                },
                {
                    'status': HTTPStatus.OK,
                    'message': statuses.changed
                }
        ),
        # Тест изменения логина и пароля при неправильном old_password
        (
                {
                    'correct_password': False,
                    'login': 'user_change_2',
                    'old_password': '123',
                    'new_login': 'user_change_new_2',
                    'new_password': '1234'
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': statuses.not_found
                }
        )
    ]
)
async def test_auth_change_password(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для изменения логина и пароля
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(data=users, login=[query_data.pop("login")], password=query_data["old_password"])
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()))

    """
    Получение access токена
    """

    access_tokens = await get_access_token(users=pg_data, is_superuser=False, roles=[])

    """
    Отправление запроса
    """

    if not query_data.pop('correct_password'):
        query_data['old_password'] = 'incorrect'

    query_data["auth"] = access_tokens[0]
    status, body = await make_request('/api/v1/auth/change-password', query_data, "PATCH")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка сообщения запроса
    """

    assert body['message'] == expected_answer['message']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тесты на получение истории пользователя
        (
                {
                    'login': 'user_history_1',
                    'password': '123',
                    'count_login': 5,
                    'page_num': 1
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 5
                }
        ),
        # Проверка пагинации при получении истории
        (
                {
                    'login': 'user_history_2',
                    'password': '123',
                    'count_login': 12,
                    'page_num': 2
                },
                {
                    'status': HTTPStatus.OK,
                    'length':  2
                }
        ),
    ]
)
async def test_auth_history(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для изменения логина и пароля
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(data=users, login=[query_data["login"]], password=query_data["password"])
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()))
    history_data = {
        'page_num': query_data.pop('page_num')
    }
    """
    Отправление запросов на вход в систему
    """

    access_token = None

    for _ in range(query_data.pop('count_login')):
        status, body = await make_request('/api/v1/auth/login', query_data, "POST")
        access_token = body['access_token']
    """
    Отправление запроса
    """

    history_data["auth"] = access_token
    status, body = await make_request('/api/v1/auth/history', history_data, "GET")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка длины запроса
    """

    assert len(body) == expected_answer['length']