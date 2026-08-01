# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/models.py
# Compiled at: 2026-05-08 13:46:57
# Size of source mod 2**32: 1759 bytes
from django.db import models
from django.conf import settings
from encrypted_model_fields.fields import EncryptedTextField

class BrokerConnection(models.Model):
    BROKER_CHOICES = [
     ('schwab', 'Charles Schwab'),
     ('webull', 'Webull'),
     ('snaptrade', 'SnapTrade')]
    STATUS_CHOICES = [
     ('connected', 'Connected'),
     ('disconnected', 'Disconnected'),
     ('error', 'Error')]
    user = models.ForeignKey((settings.AUTH_USER_MODEL),
      on_delete=(models.CASCADE),
      related_name="broker_connections")
    broker = models.CharField(max_length=20, choices=BROKER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="disconnected")
    access_token = EncryptedTextField(blank=True, default="")
    refresh_token = EncryptedTextField(blank=True, default="")
    token_expires_at = models.DateTimeField(null=True, blank=True)
    account_id = models.CharField(max_length=100, blank=True)
    buying_power = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_synced = models.DateTimeField(null=True, blank=True)
    snaptrade_user_id = models.CharField(max_length=200, blank=True)
    snaptrade_user_secret = EncryptedTextField(blank=True, default="")
    snaptrade_brokerage_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'broker')

    def __str__(self):
        return f"{self.user} — {self.broker} ({self.status})"

# okay decompiling ./brokers/__pycache__/models.cpython-37.pyc
