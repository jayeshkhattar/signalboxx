# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/migrations/0001_initial.py
# Compiled at: 2026-05-07 14:52:59
# Size of source mod 2**32: 2440 bytes
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
     migrations.CreateModel(name="Order",
       fields=[
      (
       "id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
      (
       "ticker", models.CharField(max_length=20)),
      (
       "direction", models.CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell')], max_length=4)),
      (
       "quantity", models.IntegerField()),
      (
       "order_type", models.CharField(default="market", max_length=10)),
      (
       "limit_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
      (
       "status", models.CharField(choices=[('pending', 'Pending'), ('queued', 'Queued'), ('submitted', 'Submitted'), 
        ('filled', 'Filled'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default="pending", max_length=20)),
      (
       "exec_mode", models.CharField(choices=[('auto', 'Auto'), ('confirm', 'Tap to Confirm'), ('manual', 'Manual')], default="auto", max_length=10)),
      (
       "broker_order_id", models.CharField(blank=True, max_length=100)),
      (
       "fill_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
      (
       "filled_at", models.DateTimeField(blank=True, null=True)),
      (
       "latency_ms", models.IntegerField(blank=True, null=True)),
      (
       "created_at", models.DateTimeField(auto_now_add=True))]),
     migrations.CreateModel(name="RiskSettings",
       fields=[
      (
       "id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
      (
       "max_trades_per_day", models.IntegerField(default=10)),
      (
       "daily_loss_limit", models.DecimalField(decimal_places=2, default=300, max_digits=10)),
      (
       "max_position_size", models.DecimalField(decimal_places=2, default=500, max_digits=10)),
      (
       "slippage_guard_enabled", models.BooleanField(default=True)),
      (
       "slippage_threshold_pct", models.DecimalField(decimal_places=2, default=1.5, max_digits=5)),
      (
       "kill_switch_active", models.BooleanField(default=False))])]

# okay decompiling ./execution/migrations/__pycache__/0001_initial.cpython-37.pyc
