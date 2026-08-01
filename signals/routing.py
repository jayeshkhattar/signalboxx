# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/routing.py
# Compiled at: 2026-05-07 14:47:38
# Size of source mod 2**32: 231 bytes
from django.urls import re_path
from . import consumers
websocket_urlpatterns = [
 re_path("^ws/signals/$", consumers.SignalConsumer.as_asgi()),
 re_path("^ws/trader/ingest/$", consumers.TraderSignalIngestor.as_asgi())]

# okay decompiling ./signals/__pycache__/routing.cpython-37.pyc
