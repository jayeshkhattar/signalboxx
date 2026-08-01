# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/migrations/0003_auto_20260507_2025.py
# Compiled at: 2026-05-07 15:25:34
# Size of source mod 2**32: 800 bytes
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
     migrations.swappable_dependency(settings.AUTH_USER_MODEL),
     ('signals', '0002_initial')]
    operations = [
     migrations.AddField(model_name="trader",
       name="api_key",
       field=models.CharField(blank=True, max_length=64, unique=True)),
     migrations.AddField(model_name="trader",
       name="user",
       field=models.OneToOneField(blank=True, null=True, on_delete=(django.db.models.deletion.SET_NULL), related_name="trader_profile", to=(settings.AUTH_USER_MODEL)))]

# okay decompiling ./signals/migrations/__pycache__/0003_auto_20260507_2025.cpython-37.pyc
