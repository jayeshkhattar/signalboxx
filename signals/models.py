# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/models.py
# Compiled at: 2026-05-08 16:10:20
# Size of source mod 2**32: 2601 bytes
import secrets
from django.db import models
from django.conf import settings

class Trader(models.Model):
    user = models.OneToOneField((settings.AUTH_USER_MODEL),
      null=True,
      blank=True,
      on_delete=(models.SET_NULL),
      related_name="trader_profile")
    name = models.CharField(max_length=100)
    username = models.SlugField(unique=True)
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)
        (super().save)(*args, **kwargs)

    def __str__(self):
        return self.username


class Signal(models.Model):
    DIRECTION_CHOICES = [
     ('BUY', 'Buy'), ('SELL', 'Sell')]
    trader = models.ForeignKey(Trader, on_delete=(models.CASCADE), related_name="signals")
    ticker = models.CharField(max_length=20)
    direction = models.CharField(max_length=4, choices=DIRECTION_CHOICES)
    quantity = models.IntegerField()
    price_at_signal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    strike = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry = models.DateField(null=True, blank=True)
    option_type = models.CharField(max_length=4, blank=True)
    extended_hours = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trader.username} {self.direction} {self.ticker} @ {self.created_at:%Y-%m-%d %H:%M}"


class CopyRelationship(models.Model):
    EXEC_MODE_CHOICES = [
     ('auto', 'Auto'),
     ('confirm', 'Tap to Confirm'),
     ('manual', 'Manual')]
    user = models.ForeignKey((settings.AUTH_USER_MODEL),
      on_delete=(models.CASCADE),
      related_name="copy_relationships")
    trader = models.ForeignKey(Trader, on_delete=(models.CASCADE), related_name="followers")
    is_active = models.BooleanField(default=True)
    exec_mode = models.CharField(max_length=10, choices=EXEC_MODE_CHOICES, default="auto")
    size_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'trader')

    def __str__(self):
        return f"{self.user} copying {self.trader} ({self.exec_mode})"

# okay decompiling ./signals/__pycache__/models.cpython-37.pyc
