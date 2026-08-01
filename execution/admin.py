# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/admin.py
# Compiled at: 2026-05-07 14:49:05
# Size of source mod 2**32: 621 bytes
from django.contrib import admin
from .models import Order, RiskSettings

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ticker', 'direction', 'quantity', 'status', 'exec_mode',
                    'latency_ms', 'created_at')
    list_filter = ('status', 'exec_mode', 'direction')
    search_fields = ('user__email', 'ticker', 'broker_order_id')
    readonly_fields = ('created_at', )


@admin.register(RiskSettings)
class RiskSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'max_trades_per_day', 'daily_loss_limit', 'kill_switch_active')
    list_filter = ('kill_switch_active', )

# okay decompiling ./execution/__pycache__/admin.cpython-37.pyc
