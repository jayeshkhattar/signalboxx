# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/migrations/0001_initial.py
# Compiled at: 2026-05-07 14:52:59
# Size of source mod 2**32: 2577 bytes
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
     migrations.CreateModel(name="Trader",
       fields=[
      (
       "id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
      (
       "name", models.CharField(max_length=100)),
      (
       "username", models.SlugField(unique=True)),
      (
       "is_verified", models.BooleanField(default=False)),
      (
       "bio", models.TextField(blank=True)),
      (
       "created_at", models.DateTimeField(auto_now_add=True))]),
     migrations.CreateModel(name="Signal",
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
       "price_at_signal", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
      (
       "strike", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
      (
       "expiry", models.DateField(blank=True, null=True)),
      (
       "option_type", models.CharField(blank=True, max_length=4)),
      (
       "created_at", models.DateTimeField(auto_now_add=True)),
      (
       "trader", models.ForeignKey(on_delete=(django.db.models.deletion.CASCADE), related_name="signals", to="signals.trader"))]),
     migrations.CreateModel(name="CopyRelationship",
       fields=[
      (
       "id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
      (
       "is_active", models.BooleanField(default=True)),
      (
       "exec_mode", models.CharField(choices=[('auto', 'Auto'), ('confirm', 'Tap to Confirm'), ('manual', 'Manual')], default="auto", max_length=10)),
      (
       "size_multiplier", models.DecimalField(decimal_places=2, default=1.0, max_digits=4)),
      (
       "created_at", models.DateTimeField(auto_now_add=True)),
      (
       "trader", models.ForeignKey(on_delete=(django.db.models.deletion.CASCADE), related_name="followers", to="signals.trader"))])]

# okay decompiling ./signals/migrations/__pycache__/0001_initial.cpython-37.pyc
