# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/views.py
# Compiled at: 2026-05-08 17:31:25
# Size of source mod 2**32: 10297 bytes
import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Trader, Signal, CopyRelationship
logger = logging.getLogger("signals")
from .serializers import TraderSerializer, TraderProfileSerializer, TraderRegisterSerializer, PostSignalSerializer, FollowerSerializer, SignalSerializer, CopyRelationshipSerializer, FollowSerializer

class TraderListView(generics.ListAPIView):
    queryset = Trader.objects.all().order_by("-created_at")
    serializer_class = TraderSerializer
    permission_classes = [permissions.IsAuthenticated]


class FollowTraderView(APIView):
    permission_classes = [
     permissions.IsAuthenticated]

    def post(self, request, trader_id):
        trader = _get_trader_or_404(trader_id)
        ser = FollowSerializer(data=(request.data))
        ser.is_valid(raise_exception=True)
        rel, created = CopyRelationship.objects.get_or_create(user=(request.user),
          trader=trader,
          defaults={'exec_mode':ser.validated_data["exec_mode"], 
         'size_multiplier':ser.validated_data["size_multiplier"], 
         'is_active':True})
        if not created:
            rel.is_active = True
            rel.exec_mode = ser.validated_data["exec_mode"]
            rel.size_multiplier = ser.validated_data["size_multiplier"]
            rel.save()
        action = "followed" if created else "updated follow"
        logger.info("%s | user_id=%s trader=%s exec_mode=%s multiplier=%s", action, request.user.id, trader.username, rel.exec_mode, rel.size_multiplier)
        return Response((CopyRelationshipSerializer(rel).data), status=(201 if created else 200))

    def delete(self, request, trader_id):
        trader = _get_trader_or_404(trader_id)
        updated = CopyRelationship.objects.filter(user=(request.user),
          trader=trader).update(is_active=False)
        if not updated:
            return Response(status=404)
        logger.info("Unfollowed | user_id=%s trader=%s", request.user.id, trader.username)
        return Response(status=204)


class SignalFeedView(generics.ListAPIView):
    serializer_class = SignalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        followed = CopyRelationship.objects.filter(user=(self.request.user),
          is_active=True).values_list("trader_id",
          flat=True)
        return Signal.objects.filter(trader_id__in=followed).order_by("-created_at")[:100]


def _get_trader_or_404(trader_id):
    from django.http import Http404
    try:
        return Trader.objects.get(pk=trader_id)
    except Trader.DoesNotExist:
        raise Http404


def _require_trader_profile(user):
    """Return the Trader linked to this user, or raise 403."""
    try:
        return user.trader_profile
    except Trader.DoesNotExist:
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("You do not have a trader profile.")


class TraderRegisterView(APIView):
    __doc__ = "Create a Trader profile linked to the authenticated user."
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, "trader_profile"):
            logger.debug("Trader profile already exists | user_id=%s username=%s", request.user.id, request.user.trader_profile.username)
            return Response((TraderProfileSerializer(request.user.trader_profile).data),
              status=200)
        ser = TraderRegisterSerializer(data=(request.data))
        ser.is_valid(raise_exception=True)
        trader = Trader.objects.create(user=(request.user),
          name=(ser.validated_data["name"]),
          username=(ser.validated_data["username"]),
          bio=(ser.validated_data.get("bio", "")))
        logger.info("Trader profile created | user_id=%s username=%s", request.user.id, trader.username)
        return Response((TraderProfileSerializer(trader).data), status=201)


class TraderMeView(APIView):
    __doc__ = "Return the authenticated user's trader profile."
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trader = _require_trader_profile(request.user)
        return Response(TraderProfileSerializer(trader).data)


class TraderFollowersView(generics.ListAPIView):
    __doc__ = "List all active followers of the authenticated trader."
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        trader = _require_trader_profile(self.request.user)
        return CopyRelationship.objects.filter(trader=trader, is_active=True).select_related("user")


class PostSignalView(APIView):
    __doc__ = "Trader posts a new signal via REST (fan-out happens synchronously)."
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        trader = _require_trader_profile(request.user)
        ser = PostSignalSerializer(data=(request.data))
        ser.is_valid(raise_exception=True)
        signal = Signal.objects.create(trader=trader,
          ticker=(ser.validated_data["ticker"].upper()),
          direction=(ser.validated_data["direction"]),
          quantity=(ser.validated_data["quantity"]),
          price_at_signal=(ser.validated_data.get("price_at_signal")),
          strike=(ser.validated_data.get("strike")),
          expiry=(ser.validated_data.get("expiry")),
          option_type=(ser.validated_data.get("option_type") or ""),
          extended_hours=(ser.validated_data.get("extended_hours", False)))
        logger.info("Signal posted | trader=%s ticker=%s direction=%s qty=%s signal_id=%s", trader.username, signal.ticker, signal.direction, signal.quantity, signal.id)
        from execution.engine import ExecutionEngine
        from brokers.factory import get_broker
        from brokers.base import OrderPayload
        from execution.models import Order
        engine = ExecutionEngine()
        broker_conn = request.user.broker_connections.filter(status="connected").first()
        if broker_conn:
            has_price = bool(signal.price_at_signal)
            publisher_order = Order.objects.create(user=(request.user),
              broker_connection=broker_conn,
              signal=signal,
              ticker=(signal.ticker),
              direction=(signal.direction),
              quantity=(signal.quantity),
              order_type=("limit" if has_price else "market"),
              limit_price=(signal.price_at_signal if has_price else None),
              status="queued",
              exec_mode="auto")
            engine.execute_order(publisher_order)
            logger.info("Publisher self-execution | trader=%s signal_id=%s order_id=%s status=%s", trader.username, signal.id, publisher_order.id, publisher_order.status)
        else:
            logger.info("Publisher has no connected broker — skipping self-execution | trader=%s", trader.username)
        orders = engine.process_signal(signal)
        logger.info("Signal fan-out complete | signal_id=%s follower_orders=%s", signal.id, len(orders))
        _push_signal_to_followers(signal, trader)
        exec_result = None
        if broker_conn:
            exec_result = {'status':publisher_order.status,  'broker':broker_conn.snaptrade_brokerage_name or broker_conn.broker, 
             'order_type':publisher_order.order_type, 
             'limit_price':str(publisher_order.limit_price) if (publisher_order.limit_price) else None, 
             'broker_order_id':publisher_order.broker_order_id or None, 
             'latency_ms':publisher_order.latency_ms, 
             'error':publisher_order.error_message or None}
        data = SignalSerializer(signal).data
        data["execution"] = exec_result
        return Response(data, status=201)


class TraderMySignalsView(generics.ListAPIView):
    __doc__ = "Return the authenticated trader's own published signals, newest first."
    serializer_class = SignalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        trader = _require_trader_profile(self.request.user)
        return Signal.objects.filter(trader=trader).order_by("-created_at")[:50]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        try:
            from analytics.pnl import compute_signal_lifecycle
            lifecycle = compute_signal_lifecycle(request.user)
            for item in response.data:
                item["lifecycle"] = lifecycle.get(item["id"])
        except Exception as exc:
            logger.warning("Signal lifecycle computation failed | reason=%s", exc)
        return response


class MyRelationshipsView(generics.ListAPIView):
    __doc__ = "Return the authenticated user's active copy relationships (with multipliers)."
    serializer_class = CopyRelationshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CopyRelationship.objects.filter(user=(self.request.user),
          is_active=True).select_related("trader")


def _push_signal_to_followers(signal, trader):
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    followers = CopyRelationship.objects.filter(trader=trader, is_active=True).values_list("user_id", flat=True)
    payload = {'type':"new_signal", 
     'signal_id':signal.id, 
     'ticker':signal.ticker, 
     'direction':signal.direction, 
     'quantity':signal.quantity, 
     'trader':trader.username}
    for user_id in followers:
        try:
            async_to_sync(channel_layer.group_send)(f"signals_user_{user_id}", {'type':"signal_event", 
             'payload':payload})
        except Exception:
            pass

# okay decompiling ./signals/__pycache__/views.cpython-37.pyc
