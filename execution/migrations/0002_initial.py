# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/migrations/0002_initial.py
# Compiled at: 2026-05-07 14:52:59
# Size of source mod 2**32: 1425 bytes
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
     ('signals', '0001_initial'),
     ('execution', '0001_initial'),
     migrations.swappable_dependency(settings.AUTH_USER_MODEL),
     ('brokers', '0002_initial')]
    operations = [
     migrations.AddField(model_name="risksettings",
       name="user",
       field=models.OneToOneField(on_delete=(django.db.models.deletion.CASCADE), related_name="risksettings", to=(settings.AUTH_USER_MODEL))),
     migrations.AddField(model_name="order",
       name="broker_connection",
       field=models.ForeignKey(on_delete=(django.db.models.deletion.CASCADE), related_name="orders", to="brokers.brokerconnection")),
     migrations.AddField(model_name="order",
       name="signal",
       field=models.ForeignKey(blank=True, null=True, on_delete=(django.db.models.deletion.SET_NULL), related_name="orders", to="signals.signal")),
     migrations.AddField(model_name="order",
       name="user",
       field=models.ForeignKey(on_delete=(django.db.models.deletion.CASCADE), related_name="orders", to=(settings.AUTH_USER_MODEL)))]

# okay decompiling ./execution/migrations/__pycache__/0002_initial.cpython-37.pyc
