# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/migrations/0004_signal_extended_hours.py
# Compiled at: 2026-05-08 16:11:01
# Size of source mod 2**32: 396 bytes
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
     ('signals', '0003_auto_20260507_2025')]
    operations = [
     migrations.AddField(model_name="signal",
       name="extended_hours",
       field=models.BooleanField(default=False))]

# okay decompiling ./signals/migrations/__pycache__/0004_signal_extended_hours.cpython-37.pyc
