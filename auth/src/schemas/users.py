from src.extensions import ma
from src.models.db_models import User


class UserDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


user_data_schema = UserDataSchema()
