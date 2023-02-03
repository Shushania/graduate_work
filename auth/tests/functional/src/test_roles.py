import uuid
from http import HTTPStatus

import pytest

from src.config.config import statuses
from tests.functional.testdata.pg_mapping import roles, user_roles, users
from tests.functional.testdata.validate_mapping import roles_map, user_role_map
from tests.functional.utils.helpers import (get_access_token, set_roles,
                                            set_user_roles, set_users)

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест на получение ролей
        (
                {
                    'login': 'user_list_role_1',
                    'password': '123',
                    'name': 'Тестовый 1',
                    'count_roles': 5,
                    'page_num': 1,
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 5
                }
        ),
        # Тест на пагинацию
        (
                {
                    'login': 'user_list_role_2',
                    'password': '123',
                    'name': 'Тестовый 1_1',
                    'count_roles': 12,
                    'page_num': 2
                },
                {
                    'status': HTTPStatus.OK,
                    'length': 7
                }
        )
    ]
)
async def test_roles_all(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для редактирования роли
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(
        data=users,
        login=[query_data.pop("login")],
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()) + ['is_superuser'])

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data, is_superuser=True, roles=[]))[0]

    """
    Занесение данных по ролям в БД
    """
    name = query_data.pop('name')
    for i in range(query_data.pop('count_roles')):
        pg_data = await set_roles(data=roles, name=[name + str(i)])
        await pg_write_data(data=pg_data, table='roles', columns=list(roles.keys()))

    """
    Отправление запроса 
    """

    status, body = await make_request(f'/api/v1/roles/all', query_data, "GET")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка длины запроса
    """

    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест на создание роли
        (
                {
                    'login': 'user_create_role_1',
                    'password': '123',
                    'name': 'Тестовый 2'
                },
                {
                    'status': HTTPStatus.CREATED,
                }
        ),
        # Тест на создание роли с существующим названием
        (
                {
                    'login': 'user_create_role_2',
                    'password': '123',
                    'name': 'Тестовый 2'
                },
                {
                    'status': HTTPStatus.CONFLICT,
                    'message': statuses.conflict
                }
        )
    ]
)
async def test_roles_create(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для создания роли
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(
        data=users,
        login=[query_data.pop("login")],
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()) + ['is_superuser'])

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data, is_superuser=True, roles=[]))[0]

    """
    Отправление запроса 
    """

    status, body = await make_request('/api/v1/roles/create', query_data, "POST")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    if status == HTTPStatus.CREATED:
        """
        Валидация запроса
        """

        assert list(body.keys()) == roles_map

    else:
        """
        Проверка сообщения запроса
        """

        assert body['message'] == expected_answer["message"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест на редактирование роли
        (
                {
                    'exists': True,
                    'login': 'user_update_role_1',
                    'password': '123',
                    'name': 'Тестовый 3'
                },
                {
                    'status': HTTPStatus.OK,
                }
        ),
        # Тест на редактирование несуществующей роли
        (
                {
                    'exists': False,
                    'login': 'user_update_role_2',
                    'password': '123',
                    'name': 'Тестовый 3_1'
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': statuses.not_found_role
                }
        )
    ]
)
async def test_roles_update(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для редактирования роли
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(
        data=users,
        login=[query_data.pop("login")],
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(data=pg_data, table='users', columns=list(users.keys()) + ['is_superuser'])

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data, is_superuser=True, roles=[]))[0]

    """
    Занесение данных по ролям в БД
    """

    pg_data = await set_roles(data=roles, name=[query_data["name"]])
    await pg_write_data(data=pg_data, table='roles', columns=list(roles.keys()))

    for i in range(len(pg_data)):
        query_data['name'] = query_data['name'] + ' update'

        """
        Отправление запроса 
        """

        if query_data.pop('exists'):
            status, body = await make_request(f'/api/v1/roles/update/{pg_data[i][0]}', query_data, "PATCH")
        else:
            status, body = await make_request(f'/api/v1/roles/update/{uuid.uuid4()}', query_data, "PATCH")

        """
        Проверка статуса запроса
        """

        assert status == expected_answer["status"]

        if status == HTTPStatus.OK:
            """
            Валидация запроса
            """

            assert list(body.keys()) == roles_map

        else:
            """
            Проверка сообщения запроса
            """

            assert body['message'] == expected_answer["message"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест на удаление роли
        (
                {
                    'exists': True,
                    'login': 'user_delete_role_1',
                    'password': '123',
                    'name': 'Тестовый 4'
                },
                {
                    'status': HTTPStatus.NO_CONTENT,
                }
        ),
        # Тест на удаление несуществующей роли
        (
                {
                    'exists': False,
                    'login': 'user_delete_role_2',
                    'password': '123',
                    'name': 'Тестовый 4_1'
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': statuses.not_found_role
                }
        )
    ]
)
async def test_roles_delete(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты для удаление роли
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(
        data=users,
        login=[query_data.pop("login")],
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(
        data=pg_data,
        table='users',
        columns=list(users.keys()) + ['is_superuser']
    )

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data, is_superuser=True, roles=[]))[0]

    """
    Занесение данных по ролям в БД
    """

    pg_data = await set_roles(data=roles, name=[query_data["name"]])
    await pg_write_data(data=pg_data, table='roles', columns=list(roles.keys()))

    for i in range(len(pg_data)):
        """
        Отправление запроса 
        """

        if query_data.pop('exists'):
            status, body = await make_request(f'/api/v1/roles/delete/{pg_data[i][0]}', query_data, "DELETE")
        else:
            status, body = await make_request(f'/api/v1/roles/delete/{uuid.uuid4()}', query_data, "DELETE")

        """
        Проверка статуса запроса
        """

        assert status == expected_answer["status"]

        if status != HTTPStatus.NO_CONTENT:

            """
            Проверка сообщения запроса
            """

            assert body['message'] == expected_answer["message"]


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # Тест на назначение роли пользователю
        (
                {
                    'exists': True,
                    'login': ['admin_link_role_1', 'user_link_role_1'],
                    'user_login': 'user_link_role_1',
                    'password': '123',
                    'name': 'Тестовый 5'
                },
                {
                    'status': HTTPStatus.OK,
                    'message': statuses.link_role
                }
        ),
        # Тест на назначение несуществующей роли несуществующему пользователю
        (
                {
                    'exists': False,
                    'login': ['admin_link_role_2', 'user_link_role_2'],
                    'user_login': 'user_link_role_2',
                    'password': '123',
                    'name': 'Тестовый 5_1'
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': statuses.not_found_role
                }
        )
    ]
)
async def test_roles_link(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты на назначение роли пользователю
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data = await set_users(
        data=users,
        login=query_data.pop("login"),
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(
        data=pg_data,
        table='users',
        columns=list(users.keys()) + ['is_superuser']
    )

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data, is_superuser=True, roles=[]))[0]

    """
    Занесение данных по ролям в БД
    """

    pg_data = await set_roles(data=roles, name=[query_data["name"]])
    await pg_write_data(data=pg_data, table='roles', columns=list(roles.keys()))

    """
    Отправление запроса 
    """
    if not query_data.pop('exists'):
        query_data['login_name'] = 'incorrect'
        query_data['role_name'] = 'incorrect'
    else:
        query_data['role_name'] = query_data.pop('name')
    status, body = await make_request(f'/api/v1/roles/link_user', query_data, "POST")

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
        # Тест на отвязку роли у пользователя
        (
                {
                    'exists': True,
                    'login': ['admin_unlink_role_1', 'user_unlink_role_1'],
                    'user_login': 'user_unlink_role_1',
                    'password': '123',
                    'name': 'Тестовый 6'
                },
                {
                    'status': HTTPStatus.OK,
                    'message': statuses.unlink_role
                }
        ),
        # Тест на отвязку несуществующей роли у несуществующему пользователю
        (
                {
                    'exists': False,
                    'login': ['admin_unlink_role_2', 'user_unlink_role_2'],
                    'user_login': 'user_unlink_role_2',
                    'password': '123',
                    'name': 'Тестовый 6_1'
                },
                {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': statuses.not_found_role
                }
        )
    ]
)
async def test_roles_unlink(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты на отвязку роли у пользователя
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data_users = await set_users(
        data=users,
        login=query_data.pop("login"),
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(
        data=pg_data_users,
        table='users',
        columns=list(users.keys()) + ['is_superuser']
    )

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data_users, is_superuser=True, roles=[]))[0]

    """
    Занесение данных по ролям в БД
    """

    pg_data_roles = await set_roles(data=roles, name=[query_data["name"]])
    await pg_write_data(data=pg_data_roles, table='roles', columns=list(roles.keys()))

    """
    Привязка роли к пользователю в БД
    """

    pg_data = await set_user_roles(data=user_roles, users=pg_data_users[1:], role=pg_data_roles[0][0])
    await pg_write_data(data=pg_data, table='users_roles', columns=list(user_roles.keys()))

    """
    Отправление запроса 
    """
    if not query_data.pop('exists'):
        query_data['login_name'] = 'incorrect'
        query_data['role_name'] = 'incorrect'
    else:
        query_data['role_name'] = query_data.pop('name')
    status, body = await make_request(f'/api/v1/roles/unlink_user', query_data, "POST")

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
        # Тест на получение ролей
        (
                {
                    'login': 'user_me_role_1',
                    'password': '123',
                    'name': 'Тестовый 7'
                },
                {
                    'status': HTTPStatus.OK
                }
        )
    ]
)
async def test_roles_me(query_data, expected_answer, pg_write_data, make_request):
    """
    Тесты на получение ролей
    """

    """
    Занесение данных по пользователю в БД
    """

    pg_data_users = await set_users(
        data=users,
        login=[query_data.pop("login")],
        password=query_data.pop("password"),
        is_superuser=True)
    await pg_write_data(
        data=pg_data_users,
        table='users',
        columns=list(users.keys()) + ['is_superuser']
    )

    """
    Получение access токена
    """

    query_data['auth'] = (await get_access_token(users=pg_data_users, is_superuser=True, roles=[]))[0]

    """
    Занесение данных по ролям в БД
    """

    pg_data_roles = await set_roles(data=roles, name=[query_data["name"]])
    await pg_write_data(data=pg_data_roles, table='roles', columns=list(roles.keys()))

    """
    Привязка роли к пользователю в БД
    """

    pg_data = await set_user_roles(data=user_roles, users=pg_data_users[1:], role=pg_data_roles[0][0])
    await pg_write_data(data=pg_data, table='users_roles', columns=list(user_roles.keys()))

    """
    Отправление запроса 
    """
    status, body = await make_request(f'/api/v1/roles/me', query_data, "GET")

    """
    Проверка статуса запроса
    """

    assert status == expected_answer["status"]

    """
    Проверка сообщения запроса
    """

    assert list(body.keys()) == user_role_map
