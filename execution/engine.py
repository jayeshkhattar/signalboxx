import re
import time
import logging
from decimal import Decimal
from typing import List

from django.utils import timezone
from django.db.models import Sum

from brokers.factory import get_broker
from brokers.base import OrderPayload
from .models import Order, RiskSettings

logger = logging.getLogger(__name__)


def _extract_error_message(exc_str: str) -> str:
    for pattern in [r"'detail':\s*\"([^\"]+)\"", r"'detail':\s*'([^']+)'"]:
        match = re.search(pattern, exc_str)
        if match:
            detail = match.group(1)
            detail = re.sub(r'^Trade [a-f0-9\-]+:\s*Order rejected by brokerage\s*-?\s*', '', detail)
            detail = re.sub(r'^Trade [a-f0-9\-]+:\s*', '', detail)
            return detail.strip()
    msg_match = re.search(r"'message':\s*['\"]([^'\"]+)['\"]", exc_str)
    if msg_match:
        return msg_match.group(1).strip()
    lines = [l.strip() for l in exc_str.splitlines() if l.strip()
             and not l.startswith('HTTP response')
             and not l.startswith('Reason:')]
    clean = ' '.join(lines)
    return clean[:400] if clean else exc_str[:400]


class ExecutionEngine:

    def process_signal(self, signal) -> List:
        from signals.models import CopyRelationship
        relationships = CopyRelationship.objects.filter(trader=signal.trader, is_active=True).select_related("user")
        orders = []
        for rel in relationships:
            order = self._create_order(signal, rel)
            if order:
                orders.append(order)
        return orders

    def _create_order(self, signal, relationship):
        user = relationship.user
        risk = self._get_risk_settings(user)
        if risk.kill_switch_active:
            logger.info("Kill switch active for user %s — skipping signal %s", user.id, signal.id)
            return None
        if self._daily_loss_exceeded(user, risk):
            logger.warning("Daily loss limit hit for user %s", user.id)
            return None
        if self._daily_trade_count_exceeded(user, risk):
            logger.warning("Daily trade count limit hit for user %s", user.id)
            return None
        broker_conn = user.broker_connections.filter(status="connected").first()
        if not broker_conn:
            logger.warning("No connected broker for user %s", user.id)
            return None
        quantity = max(1, int(signal.quantity * relationship.size_multiplier))
        order_type = "market"
        limit_price = None
        if risk.slippage_guard_enabled and signal.price_at_signal:
            order_type = "limit"
            limit_price = signal.price_at_signal * Decimal("1.015")
        order = Order.objects.create(
            user=user, broker_connection=broker_conn, signal=signal,
            ticker=signal.ticker, direction=signal.direction, quantity=quantity,
            order_type=order_type, limit_price=limit_price,
            size_multiplier=relationship.size_multiplier,
            status="queued", exec_mode=relationship.exec_mode,
        )
        if relationship.exec_mode == "auto":
            # Dispatch to Celery so every follower's order fires in parallel.
            # Falls back to inline execution if no broker/worker is reachable.
            try:
                from .tasks import execute_order_task
                execute_order_task.delay(order.id)
                logger.info("Order %s queued to Celery for parallel execution", order.id)
            except Exception as exc:
                logger.warning("Celery dispatch failed for order %s (%s) — running inline", order.id, exc)
                self.execute_order(order)
        elif relationship.exec_mode == "confirm":
            self._push_confirm_notification(order)
        return order

    def execute_order(self, order: Order) -> Order:
        broker = get_broker(order.broker_connection)
        payload = OrderPayload(
            ticker=order.ticker, direction=order.direction, quantity=order.quantity,
            order_type=order.order_type, limit_price=order.limit_price,
            strike=order.signal.strike if order.signal else None,
            expiry=str(order.signal.expiry) if order.signal and order.signal.expiry else None,
            option_type=order.signal.option_type if order.signal else None,
            extended_hours=order.signal.extended_hours if order.signal else False,
        )
        t0 = time.monotonic()
        try:
            result = broker.place_order(payload)
            latency_ms = int((time.monotonic() - t0) * 1000)
            order.broker_order_id = result.broker_order_id
            order.status = "submitted" if result.status == "submitted" else "rejected"
            order.latency_ms = latency_ms
            order.error_message = ""
            order.save(update_fields=["broker_order_id", "status", "latency_ms", "error_message"])
            logger.info("Order %s %s in %dms", order.id, order.status, latency_ms)
        except Exception as exc:
            exc_str = str(exc)
            signal_price = order.signal.price_at_signal if order.signal else None
            # Detect market-closed / outside-hours rejection for options
            is_market_closed = (
                "CORE_TIME" in exc_str
                or "trading hours" in exc_str.lower()
                or "cannot place orders at this moment" in exc_str.lower()
            )
            if is_market_closed:
                from datetime import date
                expiry = order.signal.expiry if order.signal else None
                is_0dte = expiry and (str(expiry) == str(date.today()))
                if is_0dte:
                    # 0DTE options expire today — GTC won't work, nothing we can do after hours
                    order.status = "rejected"
                    order.error_message = "0DTE options cannot be placed after market hours — the contract expires today."
                    order.save(update_fields=["status", "error_message"])
                    logger.warning("Order %s rejected: 0DTE after hours | expiry=%s", order.id, expiry)
                    return order
                # Future-dated option: retry as limit GTC so it queues for market open
                retry_price = signal_price or order.limit_price
                if retry_price:
                    logger.warning("Order %s: outside market hours — retrying as limit GTC @ %s", order.id, retry_price)
                    try:
                        payload.order_type = "limit"
                        payload.limit_price = retry_price
                        payload.extended_hours = True  # maps to time_in_force=GTC
                        result = broker.place_order(payload)
                        latency_ms = int((time.monotonic() - t0) * 1000)
                        order.order_type = "limit"
                        order.limit_price = retry_price
                        order.broker_order_id = result.broker_order_id
                        order.status = "submitted" if result.status == "submitted" else "rejected"
                        order.latency_ms = latency_ms
                        order.error_message = ""
                        order.save(update_fields=["order_type", "limit_price", "broker_order_id", "status", "latency_ms", "error_message"])
                        logger.info("Order %s retried as limit GTC after-hours — %s in %dms", order.id, order.status, latency_ms)
                        return order
                    except Exception as retry_exc:
                        exc_str = str(retry_exc)
                        logger.error("Order %s limit GTC retry also failed: %s", order.id, retry_exc)
                        order.status = "rejected"
                        order.error_message = _extract_error_message(exc_str)
                        order.save(update_fields=["status", "error_message"])
                        return order
                else:
                    order.status = "rejected"
                    order.error_message = "Market closed — set a Limit price to queue your order for market open."
                    order.save(update_fields=["status", "error_message"])
                    logger.warning("Order %s rejected: outside market hours, no price to retry | %s", order.id, exc_str[:200])
                    return order
            if (payload.order_type.lower() == "market" and signal_price
                and ("extended" in exc_str.lower() or "limit order" in exc_str.lower()
                     or "1119" in exc_str or "DAY_ORDER_NOT_ALLOWED" in exc_str)):
                logger.warning("Order %s: market order rejected (extended hours) — retrying as limit @ %s", order.id, signal_price)
                try:
                    payload.order_type = "limit"
                    payload.limit_price = signal_price
                    result = broker.place_order(payload)
                    latency_ms = int((time.monotonic() - t0) * 1000)
                    order.order_type = "limit"
                    order.limit_price = signal_price
                    order.broker_order_id = result.broker_order_id
                    order.status = "submitted" if result.status == "submitted" else "rejected"
                    order.latency_ms = latency_ms
                    order.error_message = ""
                    order.save(update_fields=["order_type", "limit_price", "broker_order_id", "status", "latency_ms", "error_message"])
                    logger.info("Order %s retried as limit — %s in %dms", order.id, order.status, latency_ms)
                    return order
                except Exception as retry_exc:
                    exc_str = str(retry_exc)
                    logger.error("Order %s limit retry also failed: %s", order.id, retry_exc)
            order.status = "rejected"
            order.error_message = _extract_error_message(exc_str)
            order.save(update_fields=["status", "error_message"])
            logger.error("Order %s failed: %s", order.id, exc_str)
        return order

    def activate_kill_switch(self, user):
        risk, _ = RiskSettings.objects.get_or_create(user=user)
        risk.kill_switch_active = True
        risk.save(update_fields=["kill_switch_active"])
        open_orders = Order.objects.filter(user=user, status="submitted").select_related("broker_connection")
        for order in open_orders:
            try:
                broker = get_broker(order.broker_connection)
                broker.cancel_order(order.broker_order_id)
                order.status = "cancelled"
                order.save(update_fields=["status"])
            except Exception as exc:
                logger.error("Failed to cancel order %s during kill switch: %s", order.id, exc)

    def _get_risk_settings(self, user) -> RiskSettings:
        settings, _ = RiskSettings.objects.get_or_create(user=user)
        return settings

    def _daily_loss_exceeded(self, user, risk: RiskSettings) -> bool:
        return False

    def _daily_trade_count_exceeded(self, user, risk: RiskSettings) -> bool:
        today = timezone.now().date()
        count = Order.objects.filter(user=user, created_at__date=today, status__in=["submitted", "filled"]).count()
        return count >= risk.max_trades_per_day

    def _push_confirm_notification(self, order: Order):
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        group_name = f"signals_user_{order.user_id}"
        payload = {
            "type": "confirm_required",
            "order_id": order.id,
            "ticker": order.ticker,
            "direction": order.direction,
            "quantity": order.quantity,
        }
        try:
            async_to_sync(channel_layer.group_send)(group_name, {"type": "order_event", "payload": payload})
        except Exception as exc:
            logger.error("Failed to push confirm notification for order %s: %s", order.id, exc)
