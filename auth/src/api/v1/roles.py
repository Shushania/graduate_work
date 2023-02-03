from datetime import timedelta
from http import HTTPStatus

from circuitbreaker import circuit
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_jwt,
                                get_jwt_identity, jwt_required)
from flask_restful import Api

from src.config.config import statuses
from src.db.pg import db
from src.models.db_models import Role, User, UserRole
from src.models.role_models import RoleCRUD, RoleUserLink
from src.services.decorators.admin_required import admin_required
from src.services.decorators.leaky_busket import limit_leaky_bucket
from src.services.one_role import get_role_by_id, get_role_by_name

roles = Blueprint("roles", __name__)
api = Api(roles)
jwt = JWTManager()


@roles.route("/create", methods=["POST"])
@circuit
@jwt_required()
@admin_required()
@limit_leaky_bucket
def create_role():
    """
    create_role new role
    ---
    tags:
    - ROLES
    description: Create new user role
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            name:
              type: string
              description: Role's name
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: role
          description: Create new user role
    responses:
      201:
        description: Successfully created role
        content:
          application/json:
            example:
              id: id
              name: name
      409:
        description: Creation failed
        content:
          application/json:
            example:
              status: error
              message: Role with this name already exists
    """
    role = RoleCRUD(**request.get_json())
    role_exist = get_role_by_name(db, Role, role.name)
    if role_exist:
        return make_response(
            {
                "message": statuses.conflict,
                "status": "error"
            }, HTTPStatus.CONFLICT)

    new_role = Role(name=role.name)

    db.session.add(new_role)
    db.session.commit()
    return make_response(
        {
            "id": new_role.id,
            "name": new_role.name
        }, HTTPStatus.CREATED)


@roles.route("/all", methods=["GET"])
@circuit
@jwt_required()
@admin_required()
@limit_leaky_bucket
def list_role():
    """
    List of role
    ---
    tags:
    - ROLES
    description: List of role
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
          name: role
          description: Create new user role
    responses:
      200:
        description: Successfully get roles
        content:
          application/json:
            example:
              id: id
              name: name
    """
    page_num = request.args.get("page_num",
                                default=1,
                                type=int)
    page_size = request.args.get("page_size",
                                 default=10,
                                 type=int)
    role = (
        Role
        .query
        .paginate(
            page_num,
            page_size
        )

    )
    return jsonify([
        {
            "id": line.id,
            "name": line.name,
        }
        for line in role.items
    ])


@roles.route("/update/<role_id>", methods=["PATCH"])
@circuit
@jwt_required()
@admin_required()
@limit_leaky_bucket
def update_role(role_id):
    """
    update_role  role
    ---
    tags:
    - ROLES
    description: Update user role
    parameters:
      - name: role_id
        in: path
        required: true
        type: string
        description: Role's id
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            name:
              type: string
              description: Role's new name
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: role
          description: Update user role
    responses:
      404:
        description: Role with this id doesn't exists
        content:
          application/json:
            example:
              id: id
              name: name
    """
    role_exist = get_role_by_id(db, Role, role_id)
    if role_exist:
        role_update = RoleCRUD(**request.get_json())
        db.session \
            .query(Role) \
            .filter_by(id=role_id) \
            .update({"name": role_update.name})
        db.session.commit()
        role = Role.query.filter_by(id=role_id).first()
        return jsonify(
            {
                "id": role.id,
                "name": role.name,
            }
        )
    else:
        return make_response(
            {
                "message": statuses.not_found_role,
                "status": "error"
            }, HTTPStatus.NOT_FOUND)


@roles.route("/delete/<role_id>", methods=["DELETE"])
@circuit
@jwt_required()
@admin_required()
@limit_leaky_bucket
def delete_role(role_id):
    """
    delete_role role
    ---
    tags:
    - ROLES
    description: Delete user role
    parameters:
      - name: role_id
        in: path
        required: true
        type: string
        description: Role's id
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: role
          description: Delete user role
    responses:
      204:
        description: Role is successfully deleted
      404:
        description: Role with this id doesn't exists
        content:
          application/json:
            example:
              status: error
              message: Role with this id doesn't exists
    """
    role_exist = get_role_by_id(db, Role, role_id)
    if role_exist:
        Role.query.filter_by(id=role_id).delete()
        db.session.commit()
        return make_response(
            "",
            HTTPStatus.NO_CONTENT
        )
    else:
        return make_response(
            {
                "message": statuses.not_found_role,
                "status": "error"
            }, HTTPStatus.NOT_FOUND)


@roles.route("/link_user", methods=["POST"])
@circuit
@jwt_required()
@admin_required()
@limit_leaky_bucket
def link_user():
    """
    link_user role
    ---
    tags:
    - ROLES
    description: Add role to user
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            role_name:
              type: string
              description: Role's name
            user_login:
              type: string
              description: User's login
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: role
          description: Add role to user
    responses:
      200:
        description: Role link to user successfully
        content:
          application/json:
            example:
              status: success
              message: Role link to user successfully
      404:
        description: Role or user doesn't exists
        content:
          application/json:
            example:
              status: error
              message: Role or user doesn't exists
    """
    role_user_link = RoleUserLink(**request.get_json())
    role = get_role_by_name(db, Role, role_user_link.role_name)
    user = (
        db.session
        .query(User)
        .filter(User.login == role_user_link.user_login)
        .first()

    )

    if role and user:
        new_user_role = UserRole(user_id=user.id, role_id=role.id)
        db.session.add(new_user_role)
        db.session.commit()
        return make_response(
            {
                "message": statuses.link_role,
                "status": "success"
            },
            HTTPStatus.OK
        )
    else:
        return make_response(
            {
                "message": statuses.not_found_role,
                "status": "error"
            }, HTTPStatus.NOT_FOUND)


@roles.route("/unlink_user", methods=["POST"])
@circuit
@jwt_required()
@admin_required()
@limit_leaky_bucket
def unlink_user():
    """
    unlink_user role
    ---
    tags:
    - ROLES
    description: Deler role to user
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: 'object'
          properties:
            role_name:
              type: string
              description: Role's name
            user_login:
              type: string
              description: User's login
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: role
          description: Delete role to user
    responses:
      200:
        description: Role unlink to user successfully
        content:
          application/json:
            example:
              status: success
              message: Role unlink to user successfully
      404:
        description: Role or user doesn't exists
        content:
          application/json:
            example:
              status: error
              message: Role or user doesn't exists
    """
    role_user_link = RoleUserLink(**request.get_json())
    role = (
        db.session
        .query(Role)
        .filter((Role.name == role_user_link.role_name))
        .first()
    )
    user = (
        db.session
        .query(User)
        .filter(User.login == role_user_link.user_login)
        .first()
    )

    if role and user:
        UserRole.query.filter_by(user_id=user.id, role_id=role.id).delete()
        db.session.commit()
        return make_response(
            {
                "message": statuses.unlink_role,
                "status": "success"
            },
            HTTPStatus.OK
        )
    else:
        return make_response(
            {
                "message": statuses.not_found_role,
                "status": "error"
            }, HTTPStatus.NOT_FOUND)


@roles.route("/me", methods=["GET"])
@circuit
@jwt_required()
@limit_leaky_bucket
def get_role_me():
    """
    Get user's role
    ---
    tags:
    - ROLES
    description: Get user's role
    security:
      - Bearer: []
    requestBody:
      content:
        application/json:
          name: role
          description: Create new user role
    responses:
      200:
        description: Role unlink to user successfully
        content:
          application/json:
            example:
              user: user_login
              roles: [role_name]
    """

    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first()
    return jsonify(
        {
            "user": user.login,
            "roles": [role.name for role in user.roles]
        }
    )
