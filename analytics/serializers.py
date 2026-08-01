# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/serializers.py
# Compiled at: 2026-05-07 14:49:31
# Size of source mod 2**32: 417 bytes
from rest_framework import serializers
from .models import PerformanceSnapshot

class PerformanceSnapshotSerializer(serializers.ModelSerializer):
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = PerformanceSnapshot
        fields = ('date', 'trades_total', 'trades_won', 'win_rate', 'realized_pnl',
                  'avg_latency_ms')

    def get_win_rate(self, obj):
        return obj.win_rate()

# okay decompiling ./analytics/__pycache__/serializers.cpython-37.pyc
