# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/migrations/0001_initial.py
# Compiled at: 2026-05-07 14:52:59
# Size of source mod 2**32: 1474 bytes
from django.db import migrations, models
import encrypted_model_fields.fields

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
     migrations.CreateModel(name="BrokerConnection",
       fields=[
      (
       "id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
      (
       "broker", models.CharField(choices=[('schwab', 'Charles Schwab'), ('webull', 'Webull')], max_length=20)),
      (
       "status", models.CharField(choices=[('connected', 'Connected'), ('disconnected', 'Disconnected'), ('error', 'Error')], default="disconnected", max_length=20)),
      (
       "access_token", encrypted_model_fields.fields.EncryptedTextField(blank=True, default="")),
      (
       "refresh_token", encrypted_model_fields.fields.EncryptedTextField(blank=True, default="")),
      (
       "token_expires_at", models.DateTimeField(blank=True, null=True)),
      (
       "account_id", models.CharField(blank=True, max_length=100)),
      (
       "buying_power", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
      (
       "last_synced", models.DateTimeField(blank=True, null=True)),
      (
       "created_at", models.DateTimeField(auto_now_add=True)),
      (
       "updated_at", models.DateTimeField(auto_now=True))])]

# okay decompiling ./brokers/migrations/__pycache__/0001_initial.cpython-37.pyc
