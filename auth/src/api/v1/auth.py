from datetime import timedelta
from http import HTTPStatus

from circuitbreaker import circuit
from flasgger import Swagger
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_jwt,
                                get_jwt_identity, jwt_required)
from flask_pydantic import validate
from flask_restful import Api
from werkzeug.security import generate_password_hash

from src.config.config import statuses
from src.db.pg import db
from src.db.redis import redis_db
from src.models.db_models import User, UserHistory
from src.models.user_models import (History, LoginPasswordChange, UserCreate,
                                    UserLogin)
from src.services.decorators.leaky_busket import limit_leaky_bucket

auth = Blueprint("auth", __name__)
api = Api(auth)
jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_token(jwt_header, jwt_payload):
    """
    1. вытащить токен из запроса
    2. проверить токен через редис
    """
    jti = jwt_payload["jti"]
    token = redis_db.get(jti)
    return token is not None


@auth.route("/signup", methods=["POST"])
@circuit
def signup_user():
    """
    Sign-up new user
    ---
    tags:
    - AUTH
    description: Create new user account
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            login:
              type: string
              description: Users's login
            password:
              type: string
              description: Users's password
            email:
              type: string
              description: Users's email
    requestBody:
      content:
        application/json:
          name: user
          description: username/password for registration
    responses:
      201:
        description: Successfully registration
        content:
          application/json:
            example:
              status: success
              message: New account was registered successfully
      409:
        description: Registration failed
        content:
          application/json:
            example:
              status: error
              message: The username already exists
    """
    user = UserCreate(**request.get_json())
    user_exist = (
        db.session
        .query(User)
        .filter((User.login == user.login) | (User.email == user.email))
        .first()
    )
    if user_exist:
        return make_response(
            {
                "message": statuses.conflict,
                "status": "error"
            }, HTTPStatus.CONFLICT)

    new_user = User(login=user.login, email=user.email)
    new_user.set_password(user.password)
    db.session.add(new_user)
    db.session.commit()
    return make_response(
        {
            "message": statuses.created,
            "status": "success"
        }, HTTPStatus.CREATED)


@auth.route("/login", methods=["POST"])
@circuit
def login_user():
    """
    Login user
    ---
    tags:
    - AUTH
    description: Login in user account
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            login:
              type: string
              description: Users's login
            password:
              type: string
              description: Users's password
    requestBody:
      content:
        application/json:
          name: user
          description: username/password for login
    responses:
      200:
        description: Successfully login
        content:
          application/json:
            example:
              access_token: token
              refresh_token: token
      400:
        description: Wrong password
        content:
          application/json:
            example:
              status: success
              message: Wrong password
      404:
        description: Login failed
        content:
          application/json:
            example:
              status: error
              message: User is not found
    """
    user_login = UserLogin(**request.get_json())
    user = (
        db.session
        .query(User)
        .filter(User.login == user_login.login)
        .first()
    )
    if not user:
        return make_response(
            {
                "message": statuses.not_found,
                "status": "error"
            }, HTTPStatus.NOT_FOUND)

    if user.check_password(user_login.password):
        user_info = UserHistory(
            user_id=user.id,
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.headers.get("host", ""),
        )
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                "is_superuser": user.is_superuser,
                "roles": [role.name for role in user.roles]
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        db.session.add(user_info)
        db.session.commit()
        db.session.remove()
        return jsonify(
            data
        )
    return make_response(
        {
            "message": statuses.bad_request,
            "status": "error"
        }, HTTPStatus.BAD_REQUEST)


@auth.route("/logout", methods=["DELETE"])
@circuit
@jwt_required()
@limit_leaky_bucket
def logout_user():
    """
    Logout user
    ---
    tags:
    - AUTH
    description: Logout in user account
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully logout
        content:
          application/json:
            example:
              status: success
              message: Token withdrawn successfully
    """
    jti = get_jwt()["jti"]
    redis_db.set(jti, "", ex=timedelta(seconds=1))
    return make_response(
        {
            "message": statuses.withdrawn,
            "status": "success"
        }, HTTPStatus.OK)


@auth.route("/refresh", methods=["POST"])
@circuit
@jwt_required(refresh=True)
@limit_leaky_bucket
def refresh():
    """
    Refresh token
    ---
    tags:
    - AUTH
    description: Refresh access JWT token
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully refresh token
        content:
          application/json:
            example:
              access_token: token
    """
    identity = get_jwt_identity()
    user = (
        db.session
        .query(User)
        .filter(User.id == identity)
        .first()
    )
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            "is_superuser": user.is_superuser,
            "roles": [role.name for role in user.roles]
        },
        fresh=True
    )
    return jsonify(
        {
            "access_token": access_token
        }
    )


@auth.route("/change-password", methods=["PATCH"])
@circuit
@jwt_required()
@limit_leaky_bucket
def change_password():
    """
    Login or password changed
    ---
    tags:
    - AUTH
    description: Login or password changed
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            old_password:
              type: string
              description: Old user's password
            new_password:
              type: string
              description: New users's password
            new_login:
              type: string
              description: New users's login
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: user
          description: old_password/new_password/new_login for change
    responses:
      200:
        description: Successfully Login or password changed
        content:
          application/json:
            example:
              status: success
              message: Login or password changed
      404:
        description: Login failed
        content:
          application/json:
            example:
              status: error
              message: User is not found
      400:
        description: Wrong password
        content:
          application/json:
            example:
              status: success
              message: Wrong password
    """
    body = LoginPasswordChange(**request.get_json())
    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first()
    if user is None:
        return make_response(
            {
                "message": statuses.not_found,
                "status": "error"
            }, HTTPStatus.NOT_FOUND)
    if user.check_password(body.old_password):
        updated = {}
        if body.new_password is not None:
            new_password = generate_password_hash(body.new_password)
            updated["password"] = new_password
        if body.new_login is not None:
            updated["login"] = body.new_login
        if updated:
            db.session \
                .query(User) \
                .filter_by(id=user.id) \
                .update(updated)
            db.session.commit()
            return make_response(
                {
                    "message": statuses.changed,
                    "status": "success"
                }, HTTPStatus.OK)
        else:
            make_response(
                {
                    "message": statuses.required,
                    "status": "error"
                }, HTTPStatus.BAD_REQUEST)
    return make_response(
        {
            "message": statuses.not_found,
            "status": "error"
        }, HTTPStatus.NOT_FOUND)


@auth.route("/history", methods=["GET"])
@circuit
@jwt_required()
@limit_leaky_bucket
def get_history():
    """
    Get login history
    ---
    tags:
    - AUTH
    description: Get login history
    parameters:
      - name: page_num
        in: query
        required: false
        type: int
      - name: page_size
        in: query
        required: false
        type: int
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: user
          description: Get login history
    responses:
      200:
        description: Successfully
        content:
          application/json:
            example:
              user_agent: agent
              ip_address: ip
              auth_datetime:  datetime
    """
    page_num = request.args.get("page_num",
                                default=1,
                                type=int)
    page_size = request.args.get("page_size",
                                 default=10,
                                 type=int)
    identity = get_jwt_identity()
    history = (
        UserHistory
        .query
        .filter_by(user_id=identity)
        .paginate(
            page_num,
            page_size
        )
    )
    return jsonify([
        {
            "user_agent": line.user_agent,
            "ip_address": line.ip_address,
            "auth_datetime": line.auth_datetime,
        }
        for line in history.items
    ])
