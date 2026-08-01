# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/serializers.py
# Compiled at: 2026-05-08 13:47:28
# Size of source mod 2**32: 1050 bytes
from rest_framework import serializers
from .models import BrokerConnection

class BrokerConnectionSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = BrokerConnection
        fields = ('id', 'broker', 'display_name', 'status', 'account_id', 'buying_power',
                  'last_synced', 'snaptrade_brokerage_name', 'created_at')
        read_only_fields = fields

    def get_display_name(self, obj):
        if obj.broker == "snaptrade":
            if obj.snaptrade_brokerage_name:
                return obj.snaptrade_brokerage_name
        return {'schwab':"Charles Schwab", 
         'webull':"Webull",  'snaptrade':"SnapTrade"}.get(obj.broker, obj.broker)


class WebullConnectSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField(required=False, allow_blank=True, default="")
    account_id = serializers.CharField()

# okay decompiling ./brokers/__pycache__/serializers.cpython-37.pyc
