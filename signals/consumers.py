# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/consumers.py
# Compiled at: 2026-05-07 15:26:44
# Size of source mod 2**32: 4693 bytes
import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
logger = logging.getLogger(__name__)

class SignalConsumer(AsyncWebsocketConsumer):
    __doc__ = "\n    User-facing WebSocket: ws://host/ws/signals/?token=<jwt>\n    - Joins personal channel group for real-time signal pushes.\n    - Accepts confirm_order messages (tap-to-confirm flow).\n    "

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = f"signals_user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        else:
            if data.get("type") == "confirm_order":
                await self.handle_confirm(data.get("order_id"))

    async def handle_confirm(self, order_id):
        if not order_id:
            return
        try:
            order = await self._get_queued_confirm_order(order_id)
        except Exception:
            await self.send(json.dumps({'type':"error",  'message':"Order not found"}))
            return
        else:
            from execution.engine import ExecutionEngine
            engine = ExecutionEngine()
            await database_sync_to_async(engine.execute_order)(order)
            await self.send(json.dumps({'type':"order_executed",  'order_id':order_id}))

    @database_sync_to_async
    def _get_queued_confirm_order(self, order_id):
        from execution.models import Order
        return Order.objects.select_related("broker_connection").get(id=order_id,
          user=(self.user),
          status="queued",
          exec_mode="confirm")

    async def signal_event(self, event):
        """Push new signal data to this WebSocket client."""
        await self.send(text_data=(json.dumps(event["payload"])))

    async def order_event(self, event):
        """Push order status updates (fill confirmations, etc.)."""
        await self.send(text_data=(json.dumps(event["payload"])))


class TraderSignalIngestor(AsyncWebsocketConsumer):
    __doc__ = "\n    Trader-side WebSocket: ws://host/ws/trader/ingest/\n    Traders POST signals here; the server fans out to all followers.\n    Protected by trader API key in the query string: ?api_key=<key>\n    "

    async def connect(self):
        api_key = self._get_api_key()
        self.trader = await self._authenticate_trader(api_key)
        if not self.trader:
            await self.close()
            return
        await self.accept()
        logger.info(f"Trader {self.trader.username} connected to ingestor")

    async def disconnect(self, code):
        return

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        else:
            signal = await self._save_signal(data)
            if signal:
                await self._fan_out(signal)
                await self.send(json.dumps({'type':"ack",  'signal_id':signal.id}))

    def _get_api_key(self) -> str:
        from urllib.parse import parse_qs
        qs = parse_qs(self.scope.get("query_string", b'').decode())
        keys = qs.get("api_key", [])
        if keys:
            return keys[0]
        return ""

    @database_sync_to_async
    def _authenticate_trader(self, api_key):
        if not api_key:
            return
        from signals.models import Trader
        try:
            return Trader.objects.get(api_key=api_key)
        except Trader.DoesNotExist:
            return

    @database_sync_to_async
    def _save_signal(self, data):
        from signals.models import Signal
        try:
            return Signal.objects.create(trader=(self.trader),
              ticker=(data["ticker"]),
              direction=(data["direction"]),
              quantity=(int(data["quantity"])),
              price_at_signal=(data.get("price")),
              strike=(data.get("strike")),
              expiry=(data.get("expiry")),
              option_type=(data.get("option_type", "")))
        except Exception as e:
            try:
                logger.error(f"Failed to save signal: {e}")
                return
            finally:
                e = None
                del e

    @database_sync_to_async
    def _fan_out(self, signal):
        from execution.engine import ExecutionEngine
        engine = ExecutionEngine()
        engine.process_signal(signal)

# okay decompiling ./signals/__pycache__/consumers.cpython-37.pyc
