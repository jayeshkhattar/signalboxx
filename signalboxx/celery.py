# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signalboxx/celery.py
# Compiled at: 2026-05-09 20:54:52
# Size of source mod 2**32: 228 bytes
import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "signalboxx.settings")
app = Celery("signalboxx")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# okay decompiling ./signalboxx/__pycache__/celery.cpython-37.pyc
