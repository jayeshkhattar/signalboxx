# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signalboxx/middleware.py
# Compiled at: 2026-05-09 20:54:52
# Size of source mod 2**32: 1865 bytes
import logging
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from urllib.parse import parse_qs
logger = logging.getLogger("signalboxx.auth")

@database_sync_to_async
def get_user(user_id):
    from users.models import User
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    __doc__ = "Authenticate WebSocket connections via JWT token in query string."

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b'').decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])
        if token_list:
            token = token_list[0]
            try:
                UntypedToken(token)
                decoded = jwt_decode(token, (settings.SECRET_KEY), algorithms=["HS256"])
                user_id = decoded.get("user_id")
                scope["user"] = await get_user(user_id)
                logger.debug("WebSocket auth success | user_id=%s path=%s", user_id, scope.get("path"))
            except (InvalidToken, TokenError, Exception) as exc:
                try:
                    scope["user"] = AnonymousUser()
                    logger.warning("WebSocket auth failed | path=%s reason=%s", scope.get("path"), exc)
                finally:
                    exc = None
                    del exc

        else:
            scope["user"] = AnonymousUser()
            logger.debug("WebSocket connection without token | path=%s", scope.get("path"))
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)

# okay decompiling ./signalboxx/__pycache__/middleware.cpython-37.pyc
