# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/base.py
# Compiled at: 2026-05-08 16:10:40
# Size of source mod 2**32: 1946 bytes
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class OrderPayload:
    ticker: str
    direction: str
    quantity: int
    order_type: str
    limit_price = None
    limit_price: Optional[Decimal]
    strike = None
    strike: Optional[Decimal]
    expiry = None
    expiry: Optional[str]
    option_type = None
    option_type: Optional[str]
    extended_hours = False
    extended_hours: bool


@dataclass
class OrderResult:
    broker_order_id: str
    status: str
    fill_price: Optional[Decimal]
    message: str


class BaseBroker(ABC):

    def __init__(self, connection: "BrokerConnection"):
        self.connection = connection

    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh OAuth access token. Returns True on success."""
        return

    @abstractmethod
    def get_account_info(self) -> dict:
        """Return buying power, account_id, positions."""
        return

    @abstractmethod
    def place_order(self, payload: OrderPayload) -> OrderResult:
        """Place an order. Must complete in <500ms."""
        return

    @abstractmethod
    def cancel_order(self, broker_order_id: str) -> bool:
        """Cancel an open order."""
        return

    @abstractmethod
    def get_order_status(self, broker_order_id: str) -> dict:
        """Poll order status from broker."""
        return

    def is_token_valid(self) -> bool:
        from django.utils import timezone
        return bool(self.connection.access_token and self.connection.token_expires_at and self.connection.token_expires_at > timezone.now())

    def ensure_authenticated(self):
        if not self.is_token_valid():
            success = self.refresh_token()
            if not success:
                raise RuntimeError(f"Failed to refresh token for {self.connection.broker}")

# okay decompiling ./brokers/__pycache__/base.cpython-37.pyc
