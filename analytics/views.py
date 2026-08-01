# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/views.py
# Compiled at: 2026-05-08 16:25:26
# Size of source mod 2**32: 4807 bytes
import logging
from decimal import Decimal
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from execution.models import Order
from signals.models import Signal, CopyRelationship
from .models import PerformanceSnapshot
from .serializers import PerformanceSnapshotSerializer
logger = logging.getLogger("analytics")

class PerformanceView(generics.ListAPIView):
    serializer_class = PerformanceSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PerformanceSnapshot.objects.filter(user=(self.request.user))


class PnLCalendarView(APIView):
    """Daily realized P&L (FIFO-matched) for the calendar view. Works for any user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .pnl import compute_realized_pnl
        month = request.query_params.get("month")  # "YYYY-MM"
        daily = compute_realized_pnl(request.user, month=month)
        days = {d: {"pnl": float(v["pnl"]), "trades": v["trades"]} for d, v in daily.items()}
        month_total = round(sum(v["pnl"] for v in days.values()), 2)
        total_trades = sum(v["trades"] for v in days.values())
        return Response({
            "month": month,
            "days": days,
            "month_total": month_total,
            "total_trades": total_trades,
        })


class TraderAnalyticsView(APIView):
    __doc__ = "Live analytics for the authenticated trader/publisher."
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            trader = user.trader_profile
        except Exception:
            return Response({"detail": "No trader profile."}, status=403)
        else:
            today = timezone.now().date()
            all_signals = Signal.objects.filter(trader=trader)
            signals_total = all_signals.count()
            signals_today = all_signals.filter(created_at__date=today).count()
            top_tickers = all_signals.values("ticker").annotate(count=(Count("id"))).order_by("-count")[:5]
            buys = all_signals.filter(direction="BUY").count()
            sells = all_signals.filter(direction="SELL").count()
            active_followers = CopyRelationship.objects.filter(trader=trader, is_active=True).count()
            my_orders = Order.objects.filter(user=user, signal__trader=trader)
            orders_total = my_orders.count()
            orders_submitted = my_orders.filter(status="submitted").count()
            orders_rejected = my_orders.filter(status="rejected").count()
            avg_latency = my_orders.filter(latency_ms__isnull=False).aggregate(avg=(Avg("latency_ms")))["avg"]
            copy_orders = Order.objects.filter(signal__trader=trader).exclude(user=user)
            copy_total = copy_orders.count()
            copy_submitted = copy_orders.filter(status="submitted").count()
            recent_signals = all_signals.order_by("-created_at")[:10]
            signals_detail = []
            for sig in recent_signals:
                sig_orders = Order.objects.filter(signal=sig).exclude(user=user)
                signals_detail.append({'id':sig.id, 
                 'ticker':sig.ticker, 
                 'direction':sig.direction, 
                 'quantity':sig.quantity, 
                 'price_at_signal':str(sig.price_at_signal) if (sig.price_at_signal) else None, 
                 'extended_hours':sig.extended_hours, 
                 'created_at':(sig.created_at.isoformat)(), 
                 'copies_total':(sig_orders.count)(), 
                 'copies_submitted':(sig_orders.filter(status="submitted").count)(), 
                 'copies_rejected':(sig_orders.filter(status="rejected").count)()})

            return Response({'signals':{'total':signals_total, 
              'today':signals_today, 
              'buys':buys, 
              'sells':sells, 
              'top_tickers':list(top_tickers)}, 
             'followers':{'active':active_followers, 
              'copy_orders_total':copy_total, 
              'copy_orders_submitted':copy_submitted, 
              'copy_fill_rate':round(copy_submitted / copy_total * 100, 1) if copy_total else 0}, 
             'own_execution':{'orders_total':orders_total, 
              'orders_submitted':orders_submitted, 
              'orders_rejected':orders_rejected, 
              'avg_latency_ms':round(avg_latency) if avg_latency else None}, 
             'recent_signals':signals_detail})

# okay decompiling ./analytics/__pycache__/views.cpython-37.pyc
