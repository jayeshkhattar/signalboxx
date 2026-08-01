# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/migrations/0002_initial.py
# Compiled at: 2026-05-07 14:52:59
# Size of source mod 2**32: 777 bytes
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
     ('analytics', '0001_initial'),
     migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
     migrations.AddField(model_name="performancesnapshot",
       name="user",
       field=models.ForeignKey(on_delete=(django.db.models.deletion.CASCADE), related_name="performance_snapshots", to=(settings.AUTH_USER_MODEL))),
     migrations.AlterUniqueTogether(name="performancesnapshot",
       unique_together={
      ('user', 'date')})]

# okay decompiling ./analytics/migrations/__pycache__/0002_initial.cpython-37.pyc
