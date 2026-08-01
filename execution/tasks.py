# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/execution/tasks.py
# Compiled at: 2026-05-07 14:48:42
# Size of source mod 2**32: 2450 bytes
import logging
from celery import shared_task
from django.utils import timezone
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2, default_retry_delay=1)
def execute_order_task(self, order_id: int):
    """Async order execution. Retries up to 2x on failure."""
    from .models import Order
    from .engine import ExecutionEngine
    try:
        order = Order.objects.select_related("broker_connection").get(id=order_id)
        engine = ExecutionEngine()
        engine.execute_order(order)
    except Exception as exc:
        try:
            logger.error("execute_order_task failed for order %s: %s", order_id, exc)
            raise self.retry(exc=exc)
        finally:
            exc = None
            del exc


@shared_task
def poll_order_fills():
    """
    Periodic task (every 5s via Celery Beat).
    Polls submitted orders for fill confirmation from brokers.
    """
    from .models import Order
    from brokers.factory import get_broker
    pending = Order.objects.filter(status="submitted").select_related("broker_connection")
    for order in pending:
        try:
            broker = get_broker(order.broker_connection)
            data = broker.get_order_status(order.broker_order_id)
            broker_status = data.get("status", "")
            if broker_status in ('FILLED', 'filled'):
                order.status = "filled"
                order.fill_price = data.get("averagePrice") or data.get("fillPrice")
                order.filled_at = timezone.now()
                order.save(update_fields=["status", "fill_price", "filled_at"])
                logger.info("Order %s filled at %s", order.id, order.fill_price)
        except Exception as exc:
            try:
                logger.error("Poll fill failed for order %s: %s", order.id, exc)
            finally:
                exc = None
                del exc


@shared_task
def sync_broker_balances():
    """
    Periodic task (every 5min via Celery Beat).
    Refreshes buying_power from all connected broker accounts.
    """
    from brokers.models import BrokerConnection
    from brokers.factory import get_broker
    connections = BrokerConnection.objects.filter(status="connected")
    for conn in connections:
        try:
            broker = get_broker(conn)
            info = broker.get_account_info()
            conn.buying_power = info["buying_power"]
            conn.last_synced = timezone.now()
            conn.save(update_fields=["buying_power", "last_synced"])
        except Exception as exc:
            try:
                logger.error("Balance sync failed for connection %s: %s", conn.id, exc)
            finally:
                exc = None
                del exc

# okay decompiling ./execution/__pycache__/tasks.cpython-37.pyc
