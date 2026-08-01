# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/snaptrade.py
# Compiled at: 2026-05-08 16:10:57
# Size of source mod 2**32: 2221 bytes
from decimal import Decimal
from .base import BaseBroker, OrderPayload, OrderResult
from . import snaptrade_client as st

class SnapTradeBroker(BaseBroker):
    __doc__ = "Executes orders through SnapTrade for any connected brokerage (Webull, Schwab, IBKR, etc.)."

    def refresh_token(self) -> bool:
        return True

    def is_token_valid(self) -> bool:
        return bool(self.connection.snaptrade_user_id and self.connection.snaptrade_user_secret)

    def get_account_info(self) -> dict:
        accounts = st.get_accounts(self.connection.snaptrade_user_id, self.connection.snaptrade_user_secret)
        if not accounts:
            return {}
        acc = accounts[0]
        balance = acc.get("balance", {}).get("total", {})
        return {'account_id':(acc.get)("id", ""), 
         'buying_power':(balance.get)("amount", 0), 
         'account_name':(acc.get)("name", ""), 
         'institution_name':(acc.get)("institution_name", "")}

    def place_order(self, payload: OrderPayload) -> OrderResult:
        is_option = bool(payload.option_type and payload.strike and payload.expiry)
        common = dict(
            snaptrade_user_id=self.connection.snaptrade_user_id,
            snaptrade_user_secret=self.connection.snaptrade_user_secret,
            account_id=self.connection.account_id,
            ticker=payload.ticker,
            action=payload.direction,
            quantity=payload.quantity,
            order_type=("Market" if payload.order_type.lower() == "market" else "Limit"),
            limit_price=payload.limit_price,
            extended_hours=payload.extended_hours,
        )
        if is_option:
            result = st.place_option_order(
                strike=payload.strike,
                expiry=payload.expiry,
                option_type=payload.option_type,
                **common,
            )
        else:
            result = st.place_order(**common)
        order_id = str(result.get("brokerage_order_id") or result.get("id", "snaptrade"))
        status = result.get("status", "submitted")
        return OrderResult(broker_order_id=order_id,
          status="submitted",
          fill_price=(Decimal(str(result["fill_price"])) if result.get("fill_price") else None),
          message=(str(status)))

    def cancel_order(self, broker_order_id: str) -> bool:
        return False

    def get_order_status(self, broker_order_id: str) -> dict:
        return {"status": "unknown"}

# okay decompiling ./brokers/__pycache__/snaptrade.cpython-37.pyc
