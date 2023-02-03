from functools import wraps

from flask_jwt_extended import jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_jwt_extended.view_decorators import _decode_jwt_from_request


def admin_required():

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data, jwt_header, jwt_location = _decode_jwt_from_request(
                locations=None, fresh=False
            )
            roles = jwt_data.get('roles', [])
            print(f"\n\n{roles}\n\n")
            print(f"\n\n{jwt_data.get('is_superuser')}\n\n")
            if 'Администратор' in roles or jwt_data.get('is_superuser'):
                return fn(*args, **kwargs)
            else:
                raise NoAuthorizationError("Only admin or superuser")
        return decorator

    return wrapper
