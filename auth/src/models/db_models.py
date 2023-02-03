import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import UniqueConstraint
from src.db import db


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_yandex" PARTITION OF "social_account" FOR VALUES IN ('yandex')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "social_account_google" PARTITION OF "social_account" FOR VALUES IN ('google')"""
    )


class User(db.Model):
    """
        Модель юзера
    """
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String,
                      unique=True,
                      nullable=False)
    email = db.Column(db.String(255),
                      unique=True,
                      nullable=False)
    password = db.Column(db.String,
                         nullable=False)
    is_superuser = db.Column(db.Boolean,
                             unique=False,
                             default=False)
    roles = db.relationship("Role",
                            secondary="users_roles",
                            back_populates="users")

    def set_password(self, password):
        self.password = generate_password_hash(password)
        return self

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.login}>"


class UserRole(db.Model):
    """
    Модель связки юзера и роли
    """
    __tablename__ = "users_roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id"),
        default=uuid.uuid4(),
        nullable=False,
    )
    role_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("roles.id"),
        default=uuid.uuid4(),
        nullable=False,
    )


class Role(db.Model):
    """
    Модель с ролями для юзеров
    """
    __tablename__ = "roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    name = db.Column(db.String(32), unique=True, nullable=False)
    users = db.relationship("User", secondary="users_roles", back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"


class UserHistory(db.Model):
    """Модель для истории юзеров"""

    __tablename__ = "user_history"
    __table_args__ = (
        UniqueConstraint('id', 'auth_datetime'),
        {
            'postgresql_partition_by': 'RANGE (auth_datetime)'
        }
    )

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user_agent = db.Column(db.String, nullable=True)
    ip_address = db.Column(db.String, nullable=True)
    auth_datetime = db.Column(db.DateTime, primary_key=True, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"UserHistory: {self.user_agent} - {self.auth_datetime}"


class SocialAccount(db.Model):
    __tablename__ = "social_account"
    __table_args__ = (
        UniqueConstraint('id', 'provider'),
        {
            'postgresql_partition_by': 'LIST (provider)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship(User, backref=db.backref("social_accounts", lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    provider = db.Column(db.Text, primary_key=True, nullable=False)

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"