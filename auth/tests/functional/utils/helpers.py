import uuid

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash


async def set_users(data: dict, login: list, password: str, is_superuser:bool = False) -> dict:
    pg_data = []
    for i in range(len(login)):
        data["id"]=str(uuid.uuid4())
        data["login"] = login[i]
        data["email"] = f"{login[i]}@mail.ru"
        data["password"] = generate_password_hash(password)
        pg_data.append((data["id"], data["login"], data["email"], data["password"], is_superuser))
    return pg_data


async def set_roles(data: dict, name: list) -> dict:
    pg_data = []
    for i in range(len(name)):
        data["id"]=str(uuid.uuid4())
        data["name"] = name[i]
        pg_data.append((data["id"], data["name"]))
    return pg_data


async def set_user_roles(data: dict, users: list, role:str) -> dict:
    pg_data = []
    for i in range(len(users)):
        data["id"]=str(uuid.uuid4())
        data["user_id"] = str(users[i][0])
        data["role_id"] = role
        pg_data.append((data["id"], data["user_id"], data["role_id"]))
    return pg_data


async def get_token(users: list, is_superuser: bool, roles: list, method):
    tokens = []
    for i in range(len(users)):
        tokens.append(
            method(
                identity=users[i][0],
                additional_claims={
                    "is_superuser": is_superuser,
                    "roles": roles
                }
            )
        )
    return tokens


async def get_access_token(users: list, is_superuser: bool, roles: list):
    return await get_token(users, is_superuser, roles, create_access_token)


async def get_refresh_token(users: list, is_superuser: bool, roles: list):
    return await get_token(users, is_superuser, roles, create_refresh_token)
