# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/migrations/0004_order_size_multiplier.py
# Compiled at: 2026-05-08 17:32:06
# Size of source mod 2**32: 382 bytes
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
     ('execution', '0003_order_error_message')]
    operations = [
     migrations.AddField(model_name="order",
       name="size_multiplier",
       field=models.DecimalField(max_digits=4, decimal_places=2, default="1.00"))]

# okay decompiling ./execution/migrations/__pycache__/0004_order_size_multiplier.cpython-37.pyc
