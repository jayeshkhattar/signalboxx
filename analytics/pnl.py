"""FIFO realized-P&L computation from filled orders.

Matches opening trades against closing trades in first-in-first-out order
and attributes realized P&L to the date of the *closing* trade.

Handles both long (BUY then SELL) and short (SELL then BUY) round-trips.
Options use a 100x contract multiplier; equities use 1x.
"""
from collections import defaultdict, deque
from decimal import Decimal


def _instrument_key(order):
    """Unique key for a tradable instrument. Options key includes the contract."""
    sig = order.signal
    if sig and sig.option_type and sig.strike:
        return (order.ticker, sig.option_type, str(sig.strike), str(sig.expiry)), Decimal("100")
    return (order.ticker,), Decimal("1")


def compute_realized_pnl(user, month=None):
    """Return {date_iso: {"pnl": Decimal, "trades": int}} of realized P&L.

    month: optional "YYYY-MM" filter applied to the result (FIFO still runs
    over the full history so lots opened earlier match correctly).
    """
    from execution.models import Order

    orders = (
        Order.objects.filter(
            user=user,
            status="filled",
            fill_price__isnull=False,
            filled_at__isnull=False,
        )
        .select_related("signal")
        .order_by("filled_at")
    )

    open_lots = defaultdict(deque)  # key -> deque of [signed_qty, price]
    daily = defaultdict(lambda: {"pnl": Decimal("0"), "trades": 0})

    for o in orders:
        key, mult = _instrument_key(o)
        day = o.filled_at.date().isoformat()
        daily[day]["trades"] += 1

        signed = o.quantity if o.direction == "BUY" else -o.quantity
        price = o.fill_price
        dq = open_lots[key]

        # Close existing lots of the opposite sign, FIFO.
        while signed != 0 and dq and (dq[0][0] > 0) != (signed > 0):
            lot_qty, lot_price = dq[0]
            matched = min(abs(lot_qty), abs(signed))
            if lot_qty > 0:  # closing a long position
                realized = (price - lot_price) * matched * mult
            else:            # closing a short position
                realized = (lot_price - price) * matched * mult
            daily[day]["pnl"] += realized

            if abs(lot_qty) == matched:
                dq.popleft()
            else:
                dq[0][0] = lot_qty - matched if lot_qty > 0 else lot_qty + matched
            signed = signed - matched if signed > 0 else signed + matched

        # Leftover quantity opens a new lot.
        if signed != 0:
            dq.append([signed, price])

    result = {}
    for day, v in daily.items():
        if month and not day.startswith(month):
            continue
        result[day] = {"pnl": v["pnl"], "trades": v["trades"]}
    return result


def compute_signal_lifecycle(user):
    """Per-signal trade lifecycle from the user's own filled orders, FIFO-matched.

    Returns {signal_id: {"started": iso, "status": "open"|"closed",
                         "closed_at": iso|None, "pnl": float}}.
    """
    from execution.models import Order

    orders = (
        Order.objects.filter(
            user=user,
            signal__isnull=False,
            status="filled",
            fill_price__isnull=False,
            filled_at__isnull=False,
        )
        .select_related("signal")
        .order_by("filled_at")
    )

    open_lots = defaultdict(deque)  # key -> deque of {"signal_id", "qty"(signed), "price"}
    result = {}

    for o in orders:
        key, mult = _instrument_key(o)
        sigid = o.signal_id
        signed = o.quantity if o.direction == "BUY" else -o.quantity
        price = o.fill_price
        dq = open_lots[key]

        result[sigid] = {
            "started": o.filled_at.isoformat(),
            "status": "open",
            "closed_at": None,
            "pnl": Decimal("0"),
        }

        # Close opposite-sign lots FIFO; credit P&L to both opening and closing signal.
        while signed != 0 and dq and (dq[0]["qty"] > 0) != (signed > 0):
            lot = dq[0]
            matched = min(abs(lot["qty"]), abs(signed))
            if lot["qty"] > 0:
                pnl = (price - lot["price"]) * matched * mult
            else:
                pnl = (lot["price"] - price) * matched * mult
            result[sigid]["pnl"] += pnl
            opening = result.get(lot["signal_id"])
            if opening:
                opening["pnl"] += pnl
                opening["status"] = "closed"
                opening["closed_at"] = o.filled_at.isoformat()
            if abs(lot["qty"]) == matched:
                dq.popleft()
            else:
                lot["qty"] = lot["qty"] - matched if lot["qty"] > 0 else lot["qty"] + matched
            signed = signed - matched if signed > 0 else signed + matched

        # If this order realized P&L it was itself a closing trade.
        if result[sigid]["pnl"] != 0:
            result[sigid]["status"] = "closed"
            result[sigid]["closed_at"] = o.filled_at.isoformat()

        # Leftover quantity opens a fresh lot.
        if signed != 0:
            dq.append({"signal_id": sigid, "qty": signed, "price": price})
            if result[sigid]["pnl"] == 0:
                result[sigid]["status"] = "open"

    for v in result.values():
        v["pnl"] = round(float(v["pnl"]), 2)
    return result
