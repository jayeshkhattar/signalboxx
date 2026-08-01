# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/admin.py
# Compiled at: 2026-05-07 14:49:40
# Size of source mod 2**32: 290 bytes
from django.contrib import admin
from .models import PerformanceSnapshot

@admin.register(PerformanceSnapshot)
class PerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'trades_total', 'trades_won', 'realized_pnl', 'avg_latency_ms')
    list_filter = ('date', )

# okay decompiling ./analytics/__pycache__/admin.cpython-37.pyc
