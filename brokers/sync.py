# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/sync.py
# Compiled at: 2026-05-08 15:03:53
# Size of source mod 2**32: 3147 bytes
import logging
from django.utils import timezone
logger = logging.getLogger("brokers")

def sync_snaptrade_connection(conn) -> bool:
    """
    Re-fetch accounts and balance from SnapTrade for a given BrokerConnection.
    Returns True if the connection is still live, False if it appears broken.
    Called on login so the UI always shows fresh data.
    """
    from . import snaptrade_client as st
    if not (conn.snaptrade_user_id and conn.snaptrade_user_secret):
        logger.warning("sync_snaptrade: missing credentials | conn_id=%s", conn.id)
        return False
    logger.debug("sync_snaptrade: fetching accounts | conn_id=%s snaptrade_uid=%s", conn.id, conn.snaptrade_user_id)
    try:
        holdings = st.get_accounts(conn.snaptrade_user_id, conn.snaptrade_user_secret)
    except Exception as exc:
        try:
            logger.error("sync_snaptrade: get_accounts failed | conn_id=%s reason=%s", conn.id, exc)
            conn.status = "error"
            conn.save(update_fields=["status"])
            return False
        finally:
            exc = None
            del exc

    if not holdings:
        logger.warning("sync_snaptrade: no accounts returned | conn_id=%s", conn.id)
        return True
    first = holdings[0]
    account = first.get("account", first)
    new_account_id = account.get("id", "") or conn.account_id
    new_brokerage = account.get("institution_name") or account.get("brokerage_name", "") or conn.snaptrade_brokerage_name
    changed = new_account_id != conn.account_id or new_brokerage != conn.snaptrade_brokerage_name
    conn.account_id = new_account_id
    conn.snaptrade_brokerage_name = new_brokerage
    try:
        balances = st.get_account_balances(conn.snaptrade_user_id, conn.snaptrade_user_secret, conn.account_id)
        cash = next((b for b in balances if b.get("currency", {}).get("code") == "USD"), None)
        if cash:
            new_bp = cash.get("cash", conn.buying_power)
            if new_bp != float(conn.buying_power):
                changed = True
            conn.buying_power = new_bp
    except Exception as exc:
        try:
            logger.warning("sync_snaptrade: balance fetch failed | conn_id=%s reason=%s", conn.id, exc)
        finally:
            exc = None
            del exc

    conn.status = "connected"
    conn.last_synced = timezone.now()
    conn.save(update_fields=['account_id', 'snaptrade_brokerage_name', 'buying_power', 'status', 'last_synced'])
    logger.info("sync_snaptrade: sync complete | conn_id=%s brokerage=%s account=%s buying_power=%s changed=%s", conn.id, conn.snaptrade_brokerage_name, conn.account_id, conn.buying_power, changed)
    return True


def sync_all_snaptrade_for_user(user) -> None:
    """Sync every SnapTrade BrokerConnection belonging to this user."""
    from .models import BrokerConnection
    conns = BrokerConnection.objects.filter(user=user,
      broker="snaptrade",
      status__in=[
     "connected", "error"])
    if not conns.exists():
        logger.debug("sync_all_snaptrade: no SnapTrade connections | user_id=%s", user.id)
        return
    for conn in conns:
        sync_snaptrade_connection(conn)

# okay decompiling ./brokers/__pycache__/sync.cpython-37.pyc
