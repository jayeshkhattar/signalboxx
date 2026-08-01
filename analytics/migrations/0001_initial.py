# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/migrations/0001_initial.py
# Compiled at: 2026-05-07 14:52:59
# Size of source mod 2**32: 947 bytes
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
     migrations.CreateModel(name="PerformanceSnapshot",
       fields=[
      (
       "id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
      (
       "date", models.DateField()),
      (
       "trades_total", models.IntegerField(default=0)),
      (
       "trades_won", models.IntegerField(default=0)),
      (
       "realized_pnl", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
      (
       "avg_latency_ms", models.IntegerField(blank=True, null=True)),
      (
       "created_at", models.DateTimeField(auto_now_add=True))],
       options={"ordering": ["-date"]})]

# okay decompiling ./analytics/migrations/__pycache__/0001_initial.cpython-37.pyc
