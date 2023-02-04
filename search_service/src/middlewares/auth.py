from fastapi import Request, HTTPException
import jwt
import os
import datetime
from fastapi.responses import Response
from http import HTTPStatus

class AuthMiddleware:

    def __init__(self):
        self.free_urls = os.getenv('FREE_URL', [])

    async def __call__(self, request: Request, call_next):
        if not request.url.path in self.free_urls:
            try:
                auth_token = jwt.decode(request.headers.get('Authorization').replace("Bearer ", ""), options={"verify_signature": False})
                roles = auth_token["roles"]
                is_superuser = auth_token["is_superuser"]
                now = datetime.datetime.now()
                exp = datetime.datetime.fromtimestamp(auth_token['exp'])
                if now > exp or (not is_superuser and len(roles) == 0):
                    raise Exception
            except Exception:
                return Response(status_code=HTTPStatus.UNAUTHORIZED,
                                    content="Not authorization")
        response = await call_next(request)
        return response
