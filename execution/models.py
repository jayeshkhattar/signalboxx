# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/models.py
# Compiled at: 2026-05-08 17:31:53
# Size of source mod 2**32: 2696 bytes
from django.db import models
from django.conf import settings

class Order(models.Model):
    DIRECTION_CHOICES = [
     ('BUY', 'Buy'), ('SELL', 'Sell')]
    STATUS_CHOICES = [
     ('pending', 'Pending'), 
     ('queued', 'Queued'), 
     ('submitted', 'Submitted'), 
     ('filled', 'Filled'), 
     ('rejected', 'Rejected'), 
     ('cancelled', 'Cancelled')]
    EXEC_MODE_CHOICES = [
     ('auto', 'Auto'),
     ('confirm', 'Tap to Confirm'),
     ('manual', 'Manual')]
    user = models.ForeignKey((settings.AUTH_USER_MODEL),
      on_delete=(models.CASCADE), related_name="orders")
    broker_connection = models.ForeignKey("brokers.BrokerConnection",
      on_delete=(models.CASCADE), related_name="orders")
    signal = models.ForeignKey("signals.Signal",
      null=True, blank=True, on_delete=(models.SET_NULL), related_name="orders")
    ticker = models.CharField(max_length=20)
    direction = models.CharField(max_length=4, choices=DIRECTION_CHOICES)
    quantity = models.IntegerField()
    order_type = models.CharField(max_length=10, default="market")
    limit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    exec_mode = models.CharField(max_length=10, choices=EXEC_MODE_CHOICES, default="auto")
    size_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default="1.00")
    broker_order_id = models.CharField(max_length=100, blank=True)
    fill_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    filled_at = models.DateTimeField(null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} {self.direction} {self.quantity}x{self.ticker} [{self.status}]"


class RiskSettings(models.Model):
    user = models.OneToOneField((settings.AUTH_USER_MODEL),
      on_delete=(models.CASCADE), related_name="risksettings")
    max_trades_per_day = models.IntegerField(default=10)
    daily_loss_limit = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    max_position_size = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    slippage_guard_enabled = models.BooleanField(default=True)
    slippage_threshold_pct = models.DecimalField(max_digits=5, decimal_places=2, default=1.5)
    kill_switch_active = models.BooleanField(default=False)

    def __str__(self):
        return f"RiskSettings for {self.user}"

# okay decompiling ./execution/__pycache__/models.cpython-37.pyc
