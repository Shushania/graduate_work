from flasgger import Swagger
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api

from extensions import ma
from src.api.v1.auth import auth
from src.api.v1.oauth import oauth
from src.api.v1.roles import roles
from src.config.config import settings
from src.config.jaeger import init_jaeger
from src.db.pg import db, init_db
from src.services.commands.createsuperuser import superuser

app = Flask(__name__)
api = Api(app=app)
jwt = JWTManager(app=app)
swagger = Swagger(
    app=app,
    template={
        "swagger": "2.0",
        "info": {
            "title": "Auth",
            "version": "1.0",
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
    "swagger_ui": True,
    "specs_route": "/openapi/",
    }
)
init_db(app=app)
ma.init_app(app)
app.register_blueprint(superuser)
Migrate(app, db)
app.config['OAUTH_CREDENTIALS'] = settings.oauth_credentials

init_jaeger(app)


def test():
    app.register_blueprint(auth, url_prefix="/api/v1/auth")
    app.register_blueprint(roles, url_prefix="/api/v1/roles")
    app.register_blueprint(oauth, url_prefix="/api/v1/oauth")
    app.config['TESTING'] = True
    return app


def main(flask_app):

    flask_app.register_blueprint(auth, url_prefix="/api/v1/auth")
    flask_app.register_blueprint(roles, url_prefix="/api/v1/roles")
    flask_app.register_blueprint(oauth, url_prefix="/api/v1/oauth")
    flask_app.run(debug=True, host="0.0.0.0")


@app.before_request
def before_request():
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("request id is required")


if __name__ == '__main__':
    main(flask_app=app)
