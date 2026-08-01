# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/migrations/0003_order_error_message.py
# Compiled at: 2026-05-08 16:45:22
# Size of source mod 2**32: 379 bytes
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
     ('execution', '0002_initial')]
    operations = [
     migrations.AddField(model_name="order",
       name="error_message",
       field=models.TextField(blank=True))]

# okay decompiling ./execution/migrations/__pycache__/0003_order_error_message.cpython-37.pyc
