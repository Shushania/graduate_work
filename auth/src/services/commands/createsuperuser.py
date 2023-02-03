from http import HTTPStatus

import click
from flask import Blueprint, make_response
from flask_restful import Api

from src.db.pg import db
from src.models.db_models import User

superuser = Blueprint("superuser", __name__)
api = Api(app=superuser)


@superuser.cli.command("create")
@click.argument("login")
@click.argument("email")
@click.argument("password")
def createsuperuser(login, email, password):
    user_exist = (
        db.session.query(User)
        .filter((User.login == login) | (User.email == email))
        .first()
    )
    if user_exist:
        print("The username already exists")
    else:
        _superuser = User(login=login,
                          email=email,
                          is_superuser=True)
        _superuser.set_password(password)
        db.session.add(_superuser)
        db.session.commit()
        print("Superuser was registered successfully")
