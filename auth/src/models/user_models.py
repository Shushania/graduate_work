from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    password: str


class UserCreate(UserBase):
    email: str


class UserLogin(UserBase):
    pass

class History(BaseModel):
    user_agent: str
    ip_address: str
    auth_datetime: datetime


class LoginPasswordChange(BaseModel):
    old_password: str
    new_password: str = None
    new_login: str = None