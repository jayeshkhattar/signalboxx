# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/users/migrations/0002_user_preferred_mode.py
# Compiled at: 2026-05-08 15:52:35
# Size of source mod 2**32: 468 bytes
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
     ('users', '0001_initial')]
    operations = [
     migrations.AddField(model_name="user",
       name="preferred_mode",
       field=models.CharField(choices=[('subscriber', 'Subscriber'), ('publisher', 'Publisher')], default="subscriber", max_length=20))]

# okay decompiling ./users/migrations/__pycache__/0002_user_preferred_mode.cpython-37.pyc
