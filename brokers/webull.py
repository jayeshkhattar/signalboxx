# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/webull.py
# Compiled at: 2026-05-07 14:46:04
# Size of source mod 2**32: 4314 bytes
import requests
from django.utils import timezone
from datetime import timedelta
from .base import BaseBroker, OrderPayload, OrderResult
WEBULL_PASSPORT_URL = "https://userapi.webull.com/api/passport/refreshToken"
WEBULL_API_BASE = "https://ustrade.webullfinance.com/api/trading/v1"

class WebullBroker(BaseBroker):
    __doc__ = "\n    Webull auth uses device_id + access_token obtained via the `webull` PyPI\n    package on initial login. Tokens are stored encrypted in BrokerConnection.\n    Refresh uses the refreshToken endpoint (~7-day TTL).\n    "

    def refresh_token(self) -> bool:
        resp = requests.get(WEBULL_PASSPORT_URL,
          headers={"refreshToken": (self.connection.refresh_token)},
          timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            new_access = data.get("accessToken", "")
            new_refresh = data.get("refreshToken", self.connection.refresh_token)
            if new_access:
                self.connection.access_token = new_access
                self.connection.refresh_token = new_refresh
                self.connection.token_expires_at = timezone.now() + timedelta(days=7)
                self.connection.status = "connected"
                self.connection.save(update_fields=[
                 "access_token",
                 "refresh_token",
                 "token_expires_at",
                 "status"])
                return True
        self.connection.status = "error"
        self.connection.save(update_fields=["status"])
        return False

    def _headers(self) -> dict:
        return {'Access_token':(self.connection).access_token, 
         'Content-Type':"application/json"}

    def get_account_info(self) -> dict:
        self.ensure_authenticated()
        resp = requests.get(f"{WEBULL_API_BASE}/account",
          headers=(self._headers()), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {'buying_power':(data.get)("buyingPower", 0), 
         'account_id':(self.connection).account_id}

    def place_order(self, payload: OrderPayload) -> OrderResult:
        self.ensure_authenticated()
        is_option = bool(payload.strike)
        body = {'action':payload.direction, 
         'tickerType':"2" if is_option else "1", 
         'ticker':{"symbol": (payload.ticker)}, 
         'orderType':"MKT" if (payload.order_type == "market") else "LMT", 
         'timeInForce':"DAY", 
         'quantity':payload.quantity, 
         'outsideRegularTradingHour':False}
        if payload.limit_price:
            body["lmtPrice"] = str(payload.limit_price)
        if is_option:
            body["optionExpiryDate"] = payload.expiry
            body["optionType"] = payload.option_type.upper()
            body["strikePrice"] = str(payload.strike)
        resp = requests.post(f"{WEBULL_API_BASE}/order/place",
          json=body,
          headers=(self._headers()),
          timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return OrderResult(broker_order_id=(str(data.get("orderId", ""))),
              status="submitted",
              fill_price=None,
              message="OK")
        return OrderResult(broker_order_id="",
          status="rejected",
          fill_price=None,
          message=(resp.text))

    def cancel_order(self, broker_order_id: str) -> bool:
        self.ensure_authenticated()
        resp = requests.post(f"{WEBULL_API_BASE}/order/cancel",
          json={"orderId": broker_order_id},
          headers=(self._headers()),
          timeout=5)
        return resp.status_code == 200

    def get_order_status(self, broker_order_id: str) -> dict:
        self.ensure_authenticated()
        resp = requests.get(f"{WEBULL_API_BASE}/order/{broker_order_id}",
          headers=(self._headers()),
          timeout=5)
        resp.raise_for_status()
        return resp.json()

# okay decompiling ./brokers/__pycache__/webull.cpython-37.pyc
