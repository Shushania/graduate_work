from src.extensions import ma
from src.models.db_models import Role, UserRole


class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        fields = ('id', 'name')


class UserRoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserRole
        fields = ('id', 'user_id', 'role_id')


role_schema = RoleSchema()
user_role_schema = UserRoleSchema()