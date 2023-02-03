from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src.config.config import settings

db = SQLAlchemy()


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{settings.postgres_user}:" \
                                            f"{settings.postgres_password}@{settings.postgres_host}:" \
                                            f"{settings.postgres_port}/{settings.postgres_name}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "SECRET_KEY"
    db.init_app(app)
    app.app_context().push()
    db.create_all()
