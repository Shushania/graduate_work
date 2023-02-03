from pydantic import BaseModel


class RoleCRUD(BaseModel):
    name: str

class RoleUserLink(BaseModel):
    role_name: str
    user_login: str
