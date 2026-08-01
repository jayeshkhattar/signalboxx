# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/admin.py
# Compiled at: 2026-05-07 14:47:46
# Size of source mod 2**32: 682 bytes
from django.contrib import admin
from .models import Trader, Signal, CopyRelationship

@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'is_verified', 'created_at')
    prepopulated_fields = {"username": ('name', )}


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ('trader', 'ticker', 'direction', 'quantity', 'price_at_signal',
                    'created_at')
    list_filter = ('direction', 'ticker')


@admin.register(CopyRelationship)
class CopyRelationshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'trader', 'is_active', 'exec_mode', 'size_multiplier')
    list_filter = ('is_active', 'exec_mode')

# okay decompiling ./signals/__pycache__/admin.cpython-37.pyc
