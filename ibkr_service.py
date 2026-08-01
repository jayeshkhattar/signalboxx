#!/usr/bin/env python3
"""
SignalBoxx IBKR market-depth microservice.

Holds ONE persistent ib_async connection to the IB Gateway (already running
on the VPS for the ibkr-station project) and serves option-contract DOM
(Level 2 depth) over a tiny localhost-only HTTP API.

Django proxies to this service — it is never exposed publicly.

  GET /health
  GET /dom?ticker=AAPL&expiry=2026-05-22&strike=300&right=C
"""
import threading
import logging

from flask import Flask, request, jsonify
from ib_async import IB, Option

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("ibkr_service")

IB_HOST = "127.0.0.1"
IB_PORT = 7497          # IB Gateway socket (shared with ibkr-station)
IB_CLIENT_ID = 20       # unique — ibkr-station uses 1-4
DEPTH_ROWS = 10
LISTEN_PORT = 8811

app = Flask(__name__)

_ib = IB()
_lock = threading.Lock()
_state = {"key": None}
_depth = None


def _ensure_connected():
    if not _ib.isConnected():
        log.info("Connecting to IB Gateway %s:%s ...", IB_HOST, IB_PORT)
        _ib.connect(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID, timeout=15)
        log.info("Connected. accounts=%s", _ib.managedAccounts())


@app.route("/health")
def health():
    try:
        _ensure_connected()
        return jsonify({"connected": _ib.isConnected(), "accounts": _ib.managedAccounts()})
    except Exception as exc:
        return jsonify({"connected": False, "error": str(exc)}), 503


@app.route("/dom")
def dom():
    ticker = (request.args.get("ticker") or "").upper().strip()
    expiry = (request.args.get("expiry") or "").strip().replace("-", "")
    strike_raw = request.args.get("strike")
    right = (request.args.get("right") or "C").upper()[:1]
    if not (ticker and expiry and strike_raw):
        return jsonify({"error": "ticker, expiry, strike required"}), 400
    try:
        strike = float(strike_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "bad strike"}), 400

    key = f"{ticker}|{expiry}|{strike}|{right}"
    global _depth
    with _lock:
        try:
            _ensure_connected()
            if _state["key"] != key:
                # switch the active depth subscription
                if _depth is not None:
                    try:
                        _ib.cancelMktDepth(_depth.contract, isSmartDepth=True)
                    except Exception:
                        pass
                    _depth = None
                opt = Option(ticker, expiry, strike, right, "SMART",
                             currency="USD", multiplier="100")
                qc = _ib.qualifyContracts(opt)
                if not qc:
                    return jsonify({"error": f"Option contract not found: {key}"}), 404
                _depth = _ib.reqMktDepth(qc[0], numRows=DEPTH_ROWS, isSmartDepth=True)
                _state["key"] = key
                _ib.sleep(2.0)          # let the book populate
            else:
                _ib.sleep(0.4)          # pump the loop, refresh the book

            bids = [{"price": lvl.price, "size": float(lvl.size or 0),
                     "mm": getattr(lvl, "marketMaker", "")} for lvl in _depth.domBids]
            asks = [{"price": lvl.price, "size": float(lvl.size or 0),
                     "mm": getattr(lvl, "marketMaker", "")} for lvl in _depth.domAsks]
            return jsonify({
                "key": key, "ticker": ticker, "expiry": expiry,
                "strike": strike, "right": right,
                "bids": bids, "asks": asks,
                "levels": max(len(bids), len(asks)),
            })
        except Exception as exc:
            log.exception("dom request failed")
            return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    try:
        _ensure_connected()
    except Exception as exc:
        log.warning("Initial IB connect failed (will retry on first request): %s", exc)
    # single-threaded: all IB calls run in one thread, as ib_async requires
    app.run(host="127.0.0.1", port=LISTEN_PORT, threaded=False)
