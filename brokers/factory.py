# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/factory.py
# Compiled at: 2026-05-08 14:46:03
# Size of source mod 2**32: 442 bytes
from .schwab import SchwabBroker
from .webull import WebullBroker
from .snaptrade import SnapTradeBroker
from .base import BaseBroker
BROKER_MAP = {'schwab':SchwabBroker, 
 'webull':WebullBroker, 
 'snaptrade':SnapTradeBroker}

def get_broker(connection) -> BaseBroker:
    cls = BROKER_MAP.get(connection.broker)
    if not cls:
        raise ValueError(f"Unsupported broker: {connection.broker}")
    return cls(connection)

# okay decompiling ./brokers/__pycache__/factory.cpython-37.pyc
