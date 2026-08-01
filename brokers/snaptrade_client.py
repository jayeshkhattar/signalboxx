# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/snaptrade_client.py
# Compiled at: 2026-05-08 16:12:54
# Size of source mod 2**32: 3832 bytes
import logging
from django.conf import settings
from snaptrade_client import SnapTrade
logger = logging.getLogger(__name__)

def get_client():
    return SnapTrade(client_id=(settings.SNAPTRADE_CLIENT_ID),
      consumer_key=(settings.SNAPTRADE_CONSUMER_KEY))


def register_user(user_id: str):
    """Register a new SnapTrade user. Returns (snaptrade_user_id, snaptrade_user_secret)."""
    client = get_client()
    resp = client.authentication.register_snap_trade_user(body={"userId": user_id})
    data = resp.body
    return (data["userId"], data["userSecret"])


def get_auth_link(snaptrade_user_id, snaptrade_user_secret, redirect_uri, broker=None):
    """Get the SnapTrade OAuth portal URL for connecting a brokerage with trade permissions.
    Optionally pass `broker` (slug like 'WEBULL', 'ROBINHOOD') to skip SnapTrade's broker picker."""
    client = get_client()
    kwargs = {
        "user_id": snaptrade_user_id,
        "user_secret": snaptrade_user_secret,
        "custom_redirect": redirect_uri,
        "connection_type": "trade",
    }
    if broker:
        kwargs["broker"] = broker
    resp = client.authentication.login_snap_trade_user(**kwargs)
    return resp.body.get("loginLink", "") or resp.body.get("redirectURI", "")


def get_accounts(snaptrade_user_id: str, snaptrade_user_secret: str):
    """Return list of brokerage accounts connected through SnapTrade."""
    client = get_client()
    resp = client.account_information.list_user_accounts(query_params={'userId':snaptrade_user_id, 
     'userSecret':snaptrade_user_secret})
    return resp.body or []


def get_account_balances(snaptrade_user_id: str, snaptrade_user_secret: str, account_id: str):
    client = get_client()
    resp = client.account_information.get_user_account_balance(query_params={'userId':snaptrade_user_id, 
     'userSecret':snaptrade_user_secret},
      path_params={"accountId": account_id})
    return resp.body or []


def get_positions(snaptrade_user_id: str, snaptrade_user_secret: str, account_id: str):
    """Return live holdings/positions for the account."""
    client = get_client()
    resp = client.account_information.get_user_account_positions(
        query_params={'userId': snaptrade_user_id, 'userSecret': snaptrade_user_secret},
        path_params={'accountId': account_id},
    )
    return resp.body or []


def get_recent_orders(snaptrade_user_id: str, snaptrade_user_secret: str, account_id: str):
    """Return recent orders for the account."""
    client = get_client()
    resp = client.account_information.get_user_account_orders(
        query_params={'userId': snaptrade_user_id, 'userSecret': snaptrade_user_secret},
        path_params={'accountId': account_id},
    )
    return resp.body or []


def resolve_symbol_id(snaptrade_user_id, snaptrade_user_secret, account_id, ticker):
    """Return SnapTrade's universal_symbol_id UUID for a ticker string."""
    client = get_client()
    resp = client.reference_data.symbol_search_user_account(user_id=snaptrade_user_id,
      user_secret=snaptrade_user_secret,
      account_id=account_id,
      substring=(ticker.upper()))
    for s in resp.body or []:
        if s.get("symbol", "").upper() == ticker.upper():
            return s["id"]

    raise ValueError(f"Symbol '{ticker}' not found in SnapTrade for this account")


def place_order(snaptrade_user_id, snaptrade_user_secret, account_id, ticker, action, quantity, order_type='Market', limit_price=None, extended_hours=False):
    """Place an order through SnapTrade. action = 'BUY' or 'SELL'."""
    client = get_client()
    symbol_id = resolve_symbol_id(snaptrade_user_id, snaptrade_user_secret, account_id, ticker)
    logger.debug("Resolved symbol | ticker=%s universal_symbol_id=%s", ticker, symbol_id)
    resp = client.trading.place_force_order(user_id=snaptrade_user_id,
      user_secret=snaptrade_user_secret,
      account_id=account_id,
      action=(action.upper()),
      order_type=order_type,
      time_in_force=("GTC" if extended_hours else "Day"),
      units=(float(quantity)),
      universal_symbol_id=symbol_id,
      price=(float(limit_price) if limit_price else None))
    return resp.body


def _build_occ_symbol(ticker: str, expiry, strike, option_type: str) -> str:
    """Build the OCC option symbol: ROOT(6) + YYMMDD + C/P + STRIKE*1000(8)
    Example: AAPL Jun 20 2026 $200 CALL -> 'AAPL  260620C00200000'"""
    from datetime import datetime
    if isinstance(expiry, str):
        exp_date = datetime.strptime(expiry, '%Y-%m-%d')
    else:
        exp_date = expiry
    root = ticker.upper().ljust(6)
    date_part = exp_date.strftime('%y%m%d')
    type_part = 'C' if option_type.upper() == 'CALL' else 'P'
    strike_part = str(int(float(strike) * 1000)).zfill(8)
    return f'{root}{date_part}{type_part}{strike_part}'


def place_option_order(snaptrade_user_id, snaptrade_user_secret, account_id,
                       ticker, action, quantity, strike, expiry, option_type,
                       order_type='Market', limit_price=None, extended_hours=False):
    """Place a single-leg option order through SnapTrade.
    action: 'BUY' or 'SELL' (mapped to BUY_TO_OPEN / SELL_TO_CLOSE)
    option_type: 'CALL' or 'PUT'
    expiry: 'YYYY-MM-DD' string or date object"""
    client = get_client()

    occ_symbol = _build_occ_symbol(ticker, expiry, strike, option_type)
    logger.debug("Built OCC symbol | ticker=%s strike=%s expiry=%s type=%s -> %s",
                 ticker, strike, expiry, option_type, occ_symbol)

    action_upper = action.upper()
    snap_action = 'BUY_TO_OPEN' if action_upper == 'BUY' else 'SELL_TO_CLOSE'

    legs = [{
        'instrument': {'symbol': occ_symbol, 'instrument_type': 'OPTION'},
        'action': snap_action,
        'units': int(quantity),
    }]

    snap_order_type = 'LIMIT' if order_type.lower() == 'limit' else 'MARKET'
    price_effect = 'DEBIT' if action_upper == 'BUY' else 'CREDIT'

    kwargs = {
        'user_id': snaptrade_user_id,
        'user_secret': snaptrade_user_secret,
        'account_id': account_id,
        'order_type': snap_order_type,
        'time_in_force': 'GTC' if extended_hours else 'Day',
        'legs': legs,
        'price_effect': price_effect,
    }
    if limit_price is not None:
        kwargs['limit_price'] = str(limit_price)

    resp = client.trading.place_mleg_order(**kwargs)
    return resp.body


def delete_user(snaptrade_user_id: str):
    """Remove a user from SnapTrade (called on disconnect)."""
    try:
        client = get_client()
        client.authentication.delete_snap_trade_user(query_params={"userId": snaptrade_user_id})
    except Exception as e:
        try:
            logger.warning("SnapTrade delete_user failed: %s", e)
        finally:
            e = None
            del e

# okay decompiling ./brokers/__pycache__/snaptrade_client.cpython-37.pyc
