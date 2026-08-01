# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/views.py
# Compiled at: 2026-05-07 14:48:58
# Size of source mod 2**32: 3243 bytes
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .engine import ExecutionEngine
from .models import Order, RiskSettings
from .serializers import OrderSerializer, RiskSettingsSerializer

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=(self.request.user)).order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=(self.request.user))


class OrderConfirmView(APIView):
    __doc__ = "Confirm a queued tap-to-confirm order and fire it."
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.select_related("broker_connection").get(pk=pk,
              user=(request.user),
              status="queued",
              exec_mode="confirm")
        except Order.DoesNotExist:
            return Response({"error": "Order not found or not confirmable"}, status=404)
        else:
            engine = ExecutionEngine()
            order = engine.execute_order(order)
            return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    __doc__ = "Cancel a pending or submitted order."
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.select_related("broker_connection").get(pk=pk,
              user=(request.user),
              status__in=["queued", "submitted"])
        except Order.DoesNotExist:
            return Response({"error": "Order not found or not cancellable"}, status=404)
        else:
            if order.status == "submitted":
                if order.broker_order_id:
                    from brokers.factory import get_broker
                    try:
                        broker = get_broker(order.broker_connection)
                        broker.cancel_order(order.broker_order_id)
                    except Exception as e:
                        try:
                            return Response({"error": f"Broker cancel failed: {e}"}, status=502)
                        finally:
                            e = None
                            del e

            order.status = "cancelled"
            order.save(update_fields=["status"])
            return Response(OrderSerializer(order).data)


class KillSwitchView(APIView):
    __doc__ = "Toggle the kill switch on/off."
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        activate = request.data.get("active", True)
        engine = ExecutionEngine()
        risk, _ = RiskSettings.objects.get_or_create(user=(request.user))
        if activate:
            engine.activate_kill_switch(request.user)
        else:
            risk.kill_switch_active = False
            risk.save(update_fields=["kill_switch_active"])
        return Response({"kill_switch_active": (risk.kill_switch_active)})


class RiskSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = RiskSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = RiskSettings.objects.get_or_create(user=(self.request.user))
        return obj

# okay decompiling ./execution/__pycache__/views.cpython-37.pyc


class OpenPositionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from datetime import date
        orders = (
            Order.objects.filter(user=request.user, direction='BUY', status='filled')
            .select_related('signal')
            .order_by('-filled_at')
        )
        data = []
        for o in orders:
            s = o.signal
            exp = s.expiry if s else None
            data.append({
                'id': o.id,
                'ticker': o.ticker,
                'direction': o.direction,
                'quantity': o.quantity,
                'order_type': o.order_type,
                'fill_price': str(o.fill_price) if o.fill_price else None,
                'filled_at': o.filled_at.isoformat() if o.filled_at else None,
                'created_at': o.created_at.isoformat() if o.created_at else None,
                'option_type': s.option_type if s else '',
                'strike': str(s.strike) if s and s.strike else None,
                'expiry': exp.isoformat() if exp else None,
                'expires_in_days': (exp - date.today()).days if exp else None,
                'signal_id': s.id if s else None,
            })
        return Response(data)


class ExitPositionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from .engine import ExecutionEngine
        try:
            orig = Order.objects.get(pk=pk, user=request.user, direction='BUY', status='filled')
        except Order.DoesNotExist:
            return Response({'error': 'Position not found'}, status=404)
        order_type = request.data.get('order_type', 'market')
        limit_price = request.data.get('limit_price')
        exit_order = Order.objects.create(
            user=request.user,
            signal=orig.signal,
            ticker=orig.ticker,
            direction='SELL',
            quantity=orig.quantity,
            order_type=order_type,
            limit_price=limit_price or None,
            status='pending',
        )
        try:
            engine = ExecutionEngine(request.user)
            engine.execute(exit_order)
        except Exception as e:
            exit_order.status = 'rejected'
            exit_order.error_message = str(e)
            exit_order.save()
            return Response({'error': str(e)}, status=400)
        return Response({'id': exit_order.id, 'status': exit_order.status})
