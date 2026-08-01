# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/migrations/0003_snaptrade_fields.py
# Compiled at: 2026-05-08 13:48:27
# Size of source mod 2**32: 1107 bytes
from django.db import migrations, models
import encrypted_model_fields.fields

class Migration(migrations.Migration):
    dependencies = [
     ('brokers', '0002_initial')]
    operations = [
     migrations.AddField(model_name="brokerconnection",
       name="snaptrade_brokerage_name",
       field=models.CharField(blank=True, max_length=100)),
     migrations.AddField(model_name="brokerconnection",
       name="snaptrade_user_id",
       field=models.CharField(blank=True, max_length=200)),
     migrations.AddField(model_name="brokerconnection",
       name="snaptrade_user_secret",
       field=encrypted_model_fields.fields.EncryptedTextField(blank=True, default="")),
     migrations.AlterField(model_name="brokerconnection",
       name="broker",
       field=models.CharField(choices=[('schwab', 'Charles Schwab'), ('webull', 'Webull'), ('snaptrade', 'SnapTrade')], max_length=20))]

# okay decompiling ./brokers/migrations/__pycache__/0003_snaptrade_fields.cpython-37.pyc
