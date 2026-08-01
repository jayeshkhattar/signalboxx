# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signalboxx/asgi.py
# Compiled at: 2026-05-09 20:54:57
# Size of source mod 2**32: 670 bytes
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "signalboxx.settings")
django_asgi_app = get_asgi_application()
from signals.routing import websocket_urlpatterns
from signalboxx.middleware import JWTAuthMiddlewareStack
application = ProtocolTypeRouter({'http':django_asgi_app, 
 'websocket':AllowedHostsOriginValidator(JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns)))})

# okay decompiling ./signalboxx/__pycache__/asgi.cpython-37.pyc
