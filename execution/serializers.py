# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/serializers.py
# Compiled at: 2026-05-08 17:31:56
# Size of source mod 2**32: 961 bytes
from rest_framework import serializers
from .models import Order, RiskSettings

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'ticker', 'direction', 'quantity', 'order_type', 'limit_price',
                  'status', 'exec_mode', 'broker_order_id', 'fill_price', 'filled_at',
                  'size_multiplier', 'latency_ms', 'error_message', 'created_at')
        read_only_fields = fields


class RiskSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RiskSettings
        fields = ('max_trades_per_day', 'daily_loss_limit', 'max_position_size', 'slippage_guard_enabled',
                  'slippage_threshold_pct', 'kill_switch_active')

# okay decompiling ./execution/__pycache__/serializers.cpython-37.pyc
