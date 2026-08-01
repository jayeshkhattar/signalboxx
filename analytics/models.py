# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/models.py
# Compiled at: 2026-05-07 14:49:22
# Size of source mod 2**32: 858 bytes
from django.db import models
from django.conf import settings

class PerformanceSnapshot(models.Model):
    __doc__ = "Daily P&L and win-rate snapshot per user."
    user = models.ForeignKey((settings.AUTH_USER_MODEL),
      on_delete=(models.CASCADE), related_name="performance_snapshots")
    date = models.DateField()
    trades_total = models.IntegerField(default=0)
    trades_won = models.IntegerField(default=0)
    realized_pnl = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_latency_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ["-date"]

    def win_rate(self):
        if not self.trades_total:
            return 0
        return round(self.trades_won / self.trades_total * 100, 1)

# okay decompiling ./analytics/__pycache__/models.cpython-37.pyc
