# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/schwab.py
# Compiled at: 2026-05-07 14:45:49
# Size of source mod 2**32: 4993 bytes
import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from .base import BaseBroker, OrderPayload, OrderResult
SCHWAB_API_BASE = "https://api.schwabapi.com/trader/v1"
SCHWAB_TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
SCHWAB_AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"

class SchwabBroker(BaseBroker):

    def refresh_token(self) -> bool:
        resp = requests.post(SCHWAB_TOKEN_URL,
          data={'grant_type':"refresh_token", 
         'refresh_token':(self.connection).refresh_token, 
         'client_id':settings.SCHWAB_CLIENT_ID, 
         'client_secret':settings.SCHWAB_CLIENT_SECRET},
          timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            self.connection.access_token = data["access_token"]
            self.connection.refresh_token = data.get("refresh_token", self.connection.refresh_token)
            self.connection.token_expires_at = timezone.now() + timedelta(seconds=(data["expires_in"]))
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
        return {'Authorization':f"Bearer {self.connection.access_token}", 
         'Content-Type':"application/json"}

    def get_account_info(self) -> dict:
        self.ensure_authenticated()
        resp = requests.get(f"{SCHWAB_API_BASE}/accounts/{self.connection.account_id}",
          headers=(self._headers()),
          timeout=10)
        resp.raise_for_status()
        data = resp.json()
        balances = data["securitiesAccount"]["currentBalances"]
        return {'buying_power':balances["buyingPower"], 
         'account_id':(self.connection).account_id}

    def place_order(self, payload: OrderPayload) -> OrderResult:
        self.ensure_authenticated()
        asset_type = "OPTION" if payload.strike else "EQUITY"
        symbol = _build_occ_symbol(payload.ticker, payload.expiry, payload.option_type, payload.strike) if asset_type == "OPTION" else payload.ticker
        body = {'orderType':"MARKET" if (payload.order_type == "market") else "LIMIT", 
         'session':"NORMAL", 
         'duration':"DAY", 
         'orderStrategyType':"SINGLE", 
         'orderLegCollection':[
          {'instruction':payload.direction, 
           'quantity':payload.quantity, 
           'instrument':{'symbol':symbol, 
            'assetType':asset_type}}]}
        if payload.limit_price:
            body["price"] = str(payload.limit_price)
        resp = requests.post(f"{SCHWAB_API_BASE}/accounts/{self.connection.account_id}/orders",
          json=body,
          headers=(self._headers()),
          timeout=5)
        if resp.status_code in (200, 201):
            order_id = resp.headers.get("Location", "").split("/")[-1]
            return OrderResult(broker_order_id=order_id,
              status="submitted",
              fill_price=None,
              message="OK")
        return OrderResult(broker_order_id="",
          status="rejected",
          fill_price=None,
          message=(resp.text))

    def cancel_order(self, broker_order_id: str) -> bool:
        self.ensure_authenticated()
        resp = requests.delete(f"{SCHWAB_API_BASE}/accounts/{self.connection.account_id}/orders/{broker_order_id}",
          headers=(self._headers()),
          timeout=5)
        return resp.status_code in (200, 204)

    def get_order_status(self, broker_order_id: str) -> dict:
        self.ensure_authenticated()
        resp = requests.get(f"{SCHWAB_API_BASE}/accounts/{self.connection.account_id}/orders/{broker_order_id}",
          headers=(self._headers()),
          timeout=5)
        resp.raise_for_status()
        return resp.json()


def _build_occ_symbol(ticker, expiry, option_type, strike):
    """Build OCC option symbol, e.g. NVDA240620C00580000."""
    date_part = expiry.replace("-", "")[2[:None]]
    cp = "C" if option_type.upper() == "CALL" else "P"
    strike_int = int(float(strike) * 1000)
    return f"{ticker.upper()}{date_part}{cp}{strike_int:08d}"

# okay decompiling ./brokers/__pycache__/schwab.cpython-37.pyc
