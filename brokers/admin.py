# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/admin.py
# Compiled at: 2026-05-07 14:46:41
# Size of source mod 2**32: 386 bytes
from django.contrib import admin
from .models import BrokerConnection

@admin.register(BrokerConnection)
class BrokerConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'broker', 'status', 'account_id', 'buying_power', 'last_synced')
    list_filter = ('broker', 'status')
    search_fields = ('user__email', 'account_id')
    readonly_fields = ('created_at', 'updated_at')

# okay decompiling ./brokers/__pycache__/admin.cpython-37.pyc
