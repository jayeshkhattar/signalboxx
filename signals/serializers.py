# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/serializers.py
# Compiled at: 2026-05-08 16:10:29
# Size of source mod 2**32: 4067 bytes
from decimal import Decimal
from rest_framework import serializers
from .models import Trader, Signal, CopyRelationship

class TraderSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = Trader
        fields = ('id', 'name', 'username', 'is_verified', 'bio', 'follower_count',
                  'created_at')

    def get_follower_count(self, obj):
        return obj.followers.filter(is_active=True).count()


class TraderProfileSerializer(serializers.ModelSerializer):
    __doc__ = "Full trader profile — returned to the trader themselves (includes api_key)."
    follower_count = serializers.SerializerMethodField()
    signal_count = serializers.SerializerMethodField()
    signals_today = serializers.SerializerMethodField()

    class Meta:
        model = Trader
        fields = ('id', 'name', 'username', 'is_verified', 'bio', 'api_key', 'follower_count',
                  'signal_count', 'signals_today', 'created_at')

    def get_follower_count(self, obj):
        return obj.followers.filter(is_active=True).count()

    def get_signal_count(self, obj):
        return obj.signals.count()

    def get_signals_today(self, obj):
        from django.utils import timezone
        return obj.signals.filter(created_at__date=(timezone.now().date())).count()


class TraderRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    username = serializers.SlugField(max_length=50)
    bio = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_username(self, value):
        if Trader.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value


class PostSignalSerializer(serializers.Serializer):
    DIRECTION_CHOICES = [
     "BUY", "SELL"]
    ticker = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=DIRECTION_CHOICES)
    quantity = serializers.IntegerField(min_value=1)
    price_at_signal = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    strike = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    expiry = serializers.DateField(required=False, allow_null=True)
    option_type = serializers.ChoiceField(choices=["CALL", "PUT", ""], required=False, default="", allow_null=True)
    extended_hours = serializers.BooleanField(required=False, default=False)


class FollowerSerializer(serializers.ModelSerializer):
    __doc__ = "CopyRelationship as seen by the trader (shows the follower side)."
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = CopyRelationship
        fields = ('id', 'user_email', 'user_username', 'exec_mode', 'size_multiplier',
                  'created_at')


class SignalSerializer(serializers.ModelSerializer):
    trader_username = serializers.CharField(source="trader.username", read_only=True)

    class Meta:
        model = Signal
        fields = ('id', 'trader_username', 'ticker', 'direction', 'quantity', 'price_at_signal',
                  'strike', 'expiry', 'option_type', 'extended_hours', 'created_at')


class CopyRelationshipSerializer(serializers.ModelSerializer):
    trader = TraderSerializer(read_only=True)

    class Meta:
        model = CopyRelationship
        fields = ('id', 'trader', 'is_active', 'exec_mode', 'size_multiplier', 'created_at')
        read_only_fields = ('id', 'created_at')


class FollowSerializer(serializers.Serializer):
    exec_mode = serializers.ChoiceField(choices=[
     "auto", "confirm", "manual"],
      default="auto")
    size_multiplier = serializers.DecimalField(max_digits=4,
      decimal_places=2,
      default="1.00",
      min_value=(Decimal("0.1")),
      max_value=(Decimal("10.0")))

# okay decompiling ./signals/__pycache__/serializers.cpython-37.pyc
