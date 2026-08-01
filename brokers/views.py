# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/brokers/views.py
# Compiled at: 2026-05-09 20:55:12
# Size of source mod 2**32: 15591 bytes
import base64, hashlib, logging, os, secrets, requests
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .factory import get_broker
from .models import BrokerConnection
from .serializers import BrokerConnectionSerializer, WebullConnectSerializer
from . import snaptrade_client as st
logger = logging.getLogger("brokers")
SCHWAB_AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"
SCHWAB_TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"

class SchwabConnectView(APIView):
    __doc__ = "Initiate Schwab OAuth 2.0 + PKCE flow."
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        code_verifier = secrets.token_urlsafe(64)
        digest = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
        state = f"{request.user.id}.{code_verifier}"
        params = {'response_type':"code", 
         'client_id':settings.SCHWAB_CLIENT_ID, 
         'redirect_uri':settings.SCHWAB_REDIRECT_URI, 
         'code_challenge':code_challenge, 
         'code_challenge_method':"S256", 
         'scope':"readonly trading", 
         'state':state}
        query = "&".join((f"{k}={v}" for k, v in params.items()))
        logger.info("Schwab OAuth initiated | user_id=%s", request.user.id)
        return Response({"auth_url": f"{SCHWAB_AUTH_URL}?{query}"})


class SchwabCallbackView(APIView):
    __doc__ = "Handle Schwab OAuth callback, exchange code for tokens."
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state", "")
        try:
            user_id_str, code_verifier = state.split(".", 1)
            user_id = int(user_id_str)
        except (ValueError, AttributeError):
            logger.error("Schwab callback: invalid state param | state=%s", state[:20] if state else "—")
            return redirect("/?broker=schwab&status=error")
        else:
            if code:
                if not (code_verifier and user_id):
                    logger.error("Schwab callback: missing code or verifier | user_id=%s", user_id)
                    return redirect("/?broker=schwab&status=error")
                    logger.debug("Schwab callback: exchanging code | user_id=%s", user_id)
                    resp = requests.post(SCHWAB_TOKEN_URL,
                      data={'grant_type':"authorization_code", 
                     'code':code, 
                     'redirect_uri':settings.SCHWAB_REDIRECT_URI, 
                     'client_id':settings.SCHWAB_CLIENT_ID, 
                     'client_secret':settings.SCHWAB_CLIENT_SECRET, 
                     'code_verifier':code_verifier},
                      timeout=10)
                    if resp.status_code != 200:
                        logger.error("Schwab token exchange failed | user_id=%s http_status=%s", user_id, resp.status_code)
                        return redirect("/?broker=schwab&status=error")
            else:
                data = resp.json()
                conn, created = BrokerConnection.objects.get_or_create(user_id=user_id,
                  broker="schwab")
                conn.access_token = data["access_token"]
                conn.refresh_token = data.get("refresh_token", "")
                conn.token_expires_at = timezone.now() + timedelta(seconds=(data["expires_in"]))
                conn.status = "connected"
                broker = get_broker(conn)
                try:
                    info = broker.get_account_info()
                    conn.account_id = info.get("account_id", "")
                    conn.buying_power = info.get("buying_power", 0)
                    conn.last_synced = timezone.now()
                    logger.info("Schwab connected | user_id=%s account=%s buying_power=%s", user_id, conn.account_id, conn.buying_power)
                except Exception as exc:
                    try:
                        logger.warning("Schwab account info fetch failed | user_id=%s reason=%s", user_id, exc)
                    finally:
                        exc = None
                        del exc

            conn.save()
            return redirect("/?broker=schwab&status=connected")


class WebullConnectView(APIView):
    __doc__ = "Accept pre-obtained Webull tokens (via the webull PyPI login flow)."
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = WebullConnectSerializer(data=(request.data))
        ser.is_valid(raise_exception=True)
        conn, created = BrokerConnection.objects.get_or_create(user=(request.user),
          broker="webull")
        conn.access_token = ser.validated_data["access_token"]
        conn.refresh_token = ser.validated_data["refresh_token"]
        conn.account_id = ser.validated_data["account_id"]
        conn.token_expires_at = timezone.now() + timedelta(days=7)
        conn.status = "connected"
        conn.last_synced = timezone.now()
        conn.save()
        logger.info("Webull connected | user_id=%s account=%s new=%s", request.user.id, conn.account_id, created)
        return Response((BrokerConnectionSerializer(conn).data), status=201)


class BrokerConnectionListView(generics.ListAPIView):
    serializer_class = BrokerConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BrokerConnection.objects.filter(user=(self.request.user))


class BrokerConnectionDetailView(generics.DestroyAPIView):
    serializer_class = BrokerConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BrokerConnection.objects.filter(user=(self.request.user))

    def perform_destroy(self, instance):
        instance.access_token = ""
        instance.refresh_token = ""
        instance.status = "disconnected"
        instance.save()


class BrokerSyncView(APIView):
    __doc__ = "Force-refresh buying power from broker."
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            conn = BrokerConnection.objects.get(pk=pk, user=(request.user))
        except BrokerConnection.DoesNotExist:
            return Response(status=404)
        else:
            broker = get_broker(conn)
            try:
                info = broker.get_account_info()
                conn.buying_power = info["buying_power"]
                conn.last_synced = timezone.now()
                conn.save(update_fields=["buying_power", "last_synced"])
            except Exception as e:
                try:
                    return Response({"error": (str(e))}, status=502)
                finally:
                    e = None
                    del e

            return Response(BrokerConnectionSerializer(conn).data)


class SnapTradeConnectView(APIView):
    __doc__ = "\n    Register the user with SnapTrade (idempotent) and return the\n    SnapTrade portal URL where they choose and authorise their broker.\n    Works for both subscribers and traders.\n    "
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conn, _ = BrokerConnection.objects.get_or_create(user=(request.user),
          broker="snaptrade",
          defaults={"status": "disconnected"})
        if not conn.snaptrade_user_id:
            logger.info("SnapTrade: registering new user | user_id=%s", request.user.id)
            snap_uid = f"signalboxx_{request.user.id}"
            try:
                uid, secret = st.register_user(snap_uid)
            except Exception as e:
                # Code 1010 = user already exists in SnapTrade but we lost the secret.
                # Delete the orphaned user and re-register to get a fresh secret.
                if "1010" in str(e) or "already exist" in str(e):
                    logger.warning("SnapTrade user already exists, deleting and re-registering | user_id=%s", request.user.id)
                    try:
                        st.delete_user(snap_uid)
                    except Exception:
                        pass
                    try:
                        uid, secret = st.register_user(snap_uid)
                    except Exception as e2:
                        logger.error("SnapTrade re-registration failed | user_id=%s reason=%s", request.user.id, e2)
                        return Response({"error": f"SnapTrade registration failed: {e2}"}, status=502)
                else:
                    logger.error("SnapTrade registration failed | user_id=%s reason=%s", request.user.id, e)
                    return Response({"error": f"SnapTrade registration failed: {e}"}, status=502)

            conn.snaptrade_user_id = uid
            conn.snaptrade_user_secret = secret
            conn.save(update_fields=["snaptrade_user_id", "snaptrade_user_secret"])
            logger.debug("SnapTrade user registered | user_id=%s snaptrade_uid=%s", request.user.id, uid)
        else:
            logger.debug("SnapTrade: existing user, generating auth link | user_id=%s", request.user.id)
        redirect_uri = f"{settings.SNAPTRADE_REDIRECT_URI}?uid={conn.snaptrade_user_id}"
        broker_slug = request.query_params.get("broker") or None
        try:
            auth_url = st.get_auth_link(conn.snaptrade_user_id, conn.snaptrade_user_secret, redirect_uri, broker=broker_slug)
        except Exception as e:
            try:
                logger.error("SnapTrade auth link failed | user_id=%s reason=%s", request.user.id, e)
                return Response({"error": f"Failed to get auth link: {e}"}, status=502)
            finally:
                e = None
                del e

        logger.info("SnapTrade OAuth initiated | user_id=%s", request.user.id)
        return Response({"auth_url": auth_url})


class SnapTradeCallbackView(APIView):
    __doc__ = "\n    SnapTrade redirects here after the user connects their broker.\n    We fetch their accounts, pick the first one, and store the details.\n    "
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        raw_status = request.query_params.get("status", "")
        if raw_status.upper() != "SUCCESS":
            logger.warning("SnapTrade callback: non-success status | status=%s", raw_status)
            return redirect("/?broker=snaptrade&status=error")
        snaptrade_user_id = request.query_params.get("uid")
        if not snaptrade_user_id:
            logger.error("SnapTrade callback: missing uid param")
            return redirect("/?broker=snaptrade&status=error")
        try:
            conn = BrokerConnection.objects.get(broker="snaptrade",
              snaptrade_user_id=snaptrade_user_id)
        except BrokerConnection.DoesNotExist:
            logger.error("SnapTrade callback: no BrokerConnection found | snaptrade_uid=%s", snaptrade_user_id)
            return redirect("/?broker=snaptrade&status=error")
        else:
            logger.debug("SnapTrade callback: fetching accounts | snaptrade_uid=%s", snaptrade_user_id)
            try:
                holdings = st.get_accounts(conn.snaptrade_user_id, conn.snaptrade_user_secret)
            except Exception as e:
                try:
                    logger.error("SnapTrade get_accounts failed | snaptrade_uid=%s reason=%s", snaptrade_user_id, e)
                    return redirect("/?broker=snaptrade&status=error")
                finally:
                    e = None
                    del e

            if holdings:
                first = holdings[0]
                account = first.get("account", first)
                conn.account_id = account.get("id", "")
                brokerage = account.get("institution_name") or account.get("brokerage_name", "")
                conn.snaptrade_brokerage_name = brokerage
                logger.info("SnapTrade account found | snaptrade_uid=%s brokerage=%s account=%s", snaptrade_user_id, brokerage, conn.account_id)
                try:
                    balances = st.get_account_balances(conn.snaptrade_user_id, conn.snaptrade_user_secret, conn.account_id)
                    cash = next((b for b in balances if b.get("currency", {}).get("code") == "USD"), None)
                    if cash:
                        conn.buying_power = cash.get("buying_power") or cash.get("cash", 0)
                        logger.debug("SnapTrade balance fetched | snaptrade_uid=%s buying_power=%s", snaptrade_user_id, conn.buying_power)
                except Exception as exc:
                    try:
                        logger.warning("SnapTrade balance fetch failed | snaptrade_uid=%s reason=%s", snaptrade_user_id, exc)
                    finally:
                        exc = None
                        del exc

            else:
                logger.warning("SnapTrade callback: no accounts returned | snaptrade_uid=%s", snaptrade_user_id)
            conn.status = "connected"
            conn.last_synced = timezone.now()
            conn.save()
            logger.info("SnapTrade connected | user_id=%s brokerage=%s", conn.user_id, conn.snaptrade_brokerage_name)
            return redirect("/?broker=snaptrade&status=connected")


class SnapTradeDisconnectView(APIView):
    __doc__ = "Disconnect SnapTrade — clears credentials and optionally deletes SnapTrade user."
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        try:
            conn = BrokerConnection.objects.get(user=(request.user), broker="snaptrade")
        except BrokerConnection.DoesNotExist:
            return Response(status=404)
        else:
            snaptrade_uid = conn.snaptrade_user_id
            if snaptrade_uid:
                logger.info("SnapTrade disconnect | user_id=%s snaptrade_uid=%s", request.user.id, snaptrade_uid)
                st.delete_user(snaptrade_uid)
            conn.snaptrade_user_id = ""
            conn.snaptrade_user_secret = ""
            conn.snaptrade_brokerage_name = ""
            conn.account_id = ""
            conn.status = "disconnected"
            conn.save()
            logger.info("SnapTrade disconnected | user_id=%s", request.user.id)
            return Response(status=204)


_YF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


def _yf_get(url, params=None, timeout=10):
    """GET a Yahoo Finance JSON endpoint. Returns parsed dict or raises."""
    resp = requests.get(url, params=params, headers=_YF_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


class QuoteView(APIView):
    """Real-time quote via Yahoo Finance chart API (no extra dependency)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticker):
        ticker = ticker.upper().strip()
        # Primary: Yahoo chart API (richest fields when reachable)
        try:
            data = _yf_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}")
            result = (data.get("chart", {}).get("result") or [])
            if result:
                meta = result[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                if price is not None:
                    prev_close = meta.get("chartPreviousClose") or meta.get("previousClose") or price
                    change = round(float(price) - float(prev_close), 2)
                    change_pct = round((change / float(prev_close)) * 100, 2) if prev_close else 0
                    return Response({
                        "ticker": meta.get("symbol", ticker),
                        "name": meta.get("longName") or meta.get("shortName") or ticker,
                        "price": float(price),
                        "after_hours_price": meta.get("postMarketPrice"),
                        "change": change,
                        "change_pct": change_pct,
                        "open": meta.get("regularMarketOpen") or meta.get("chartPreviousClose"),
                        "high": meta.get("regularMarketDayHigh"),
                        "low": meta.get("regularMarketDayLow"),
                        "volume": meta.get("regularMarketVolume"),
                        "week_52_high": meta.get("fiftyTwoWeekHigh"),
                        "week_52_low": meta.get("fiftyTwoWeekLow"),
                        "source": "yahoo",
                    })
        except Exception as exc:
            logger.info("Yahoo quote unavailable, falling back to CBOE | ticker=%s error=%s", ticker, exc)

        # Fallback: CBOE delayed feed (price + change only)
        data = _fetch_cboe_options(ticker)
        if data and (data.get("current_price") or data.get("close")):
            price = float(data.get("current_price") or data.get("close"))
            prev_close = float(data.get("close") or price)
            change = round(price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
            return Response({
                "ticker": ticker, "name": ticker, "price": price,
                "after_hours_price": None, "change": change, "change_pct": change_pct,
                "open": None, "high": None, "low": None, "volume": None,
                "source": "cboe",
            })
        return Response({"detail": f"No quote data for '{ticker}'."}, status=404)


def _parse_occ(sym):
    """Parse an OCC option symbol like 'AAPL260515C00005000' → (expiry, cp, strike).
    Parsed from the right so it works regardless of root length."""
    strike = int(sym[-8:]) / 1000.0
    cp = sym[-9]
    yymmdd = sym[-15:-9]
    expiry = "20%s-%s-%s" % (yymmdd[0:2], yymmdd[2:4], yymmdd[4:6])
    return expiry, cp, strike


def _opt_row_cboe(c):
    """Compress a CBOE option contract into ladder-row fields."""
    iv = c.get("iv")
    delta = c.get("delta")
    return {
        "bid": c.get("bid"),
        "ask": c.get("ask"),
        "last": c.get("last_trade_price"),
        "volume": int(c.get("volume") or 0),
        "oi": int(c.get("open_interest") or 0),
        "iv": round(iv * 100, 1) if iv else None,
        "delta": round(delta, 3) if delta is not None else None,
    }


def _fetch_cboe_options(ticker):
    """Fetch the CBOE delayed options feed. Returns the 'data' dict or None.
    Tries the plain symbol first, then the underscore-prefixed index form."""
    for sym in (ticker, "_" + ticker):
        try:
            resp = requests.get(
                f"https://cdn.cboe.com/api/global/delayed_quotes/options/{sym}.json",
                headers=_YF_HEADERS, timeout=12)
            if resp.status_code == 200:
                return resp.json().get("data", {})
        except Exception as exc:
            logger.warning("CBOE options fetch failed | ticker=%s error=%s", ticker, exc)
    return None


class OptionsChainView(APIView):
    """Options chain ladder via CBOE's free delayed-quotes feed.

    GET /api/brokers/options-chain/<ticker>/?expiry=YYYY-MM-DD
    Returns available expiries + a strike ladder (calls / strike / puts),
    each side carrying bid/ask/last/volume/OI/IV/delta.
    Data is ~15 min delayed — the feed is isolated in _fetch_cboe_options()
    so it can be swapped for a real-time provider (ThetaData/Polygon) later.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticker):
        ticker = ticker.upper().strip()
        data = _fetch_cboe_options(ticker)
        if not data:
            return Response({"error": f"No options data for '{ticker}'."}, status=404)

        underlying = data.get("current_price") or data.get("close")
        contracts = data.get("options", []) or []

        by_expiry = {}
        for c in contracts:
            sym = c.get("option", "")
            if len(sym) < 16:
                continue
            try:
                expiry, cp, strike = _parse_occ(sym)
            except (ValueError, IndexError):
                continue
            slot = by_expiry.setdefault(expiry, {})
            row = slot.setdefault(strike, {"strike": strike, "call": None, "put": None})
            row["call" if cp == "C" else "put"] = _opt_row_cboe(c)

        expiries = sorted(by_expiry.keys())
        if not expiries:
            return Response({"error": f"No options data for '{ticker}'."}, status=404)

        chosen = request.query_params.get("expiry")
        if chosen not in by_expiry:
            chosen = expiries[0]
        ladder = [by_expiry[chosen][k] for k in sorted(by_expiry[chosen].keys())]

        return Response({
            "ticker": ticker,
            "expiries": expiries,
            "expiry": chosen,
            "underlying_price": underlying,
            "ladder": ladder,
        })


class BrokerPositionsView(APIView):
    """Live positions fetched directly from the connected broker via SnapTrade."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conn = BrokerConnection.objects.filter(user=request.user, status='connected').first()
        if not conn or not conn.snaptrade_user_id:
            return Response([], status=200)
        try:
            raw = st.get_positions(conn.snaptrade_user_id, conn.snaptrade_user_secret, conn.account_id)
        except Exception as e:
            return Response({'error': str(e)}, status=502)

        positions = []
        for p in (raw if isinstance(raw, list) else []):
            sym = p.get('symbol') or {}
            underlying = sym.get('symbol') or {}
            opt_sym = sym.get('option_symbol') or {}
            is_option = bool(opt_sym)
            positions.append({
                'ticker': underlying.get('ticker') or sym.get('ticker') or '',
                'description': sym.get('description') or '',
                'quantity': p.get('units', 0),
                'open_pnl': p.get('open_pnl'),
                'average_purchase_price': p.get('average_purchase_price'),
                'current_price': p.get('price'),
                'market_value': p.get('market_value'),
                'is_option': is_option,
                'option_type': opt_sym.get('option_type', '').upper() if is_option else '',
                'strike': opt_sym.get('strike_price') if is_option else None,
                'expiry': opt_sym.get('expiration_date') if is_option else None,
            })
        return Response(positions)


class BrokerOrdersView(APIView):
    """Recent orders fetched directly from the connected broker via SnapTrade."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conn = BrokerConnection.objects.filter(user=request.user, status='connected').first()
        if not conn or not conn.snaptrade_user_id:
            return Response([], status=200)
        try:
            raw = st.get_recent_orders(conn.snaptrade_user_id, conn.snaptrade_user_secret, conn.account_id)
        except Exception as e:
            return Response({'error': str(e)}, status=502)

        orders = []
        for o in (raw if isinstance(raw, list) else []):
            opt_sym   = o.get('option_symbol') or {}
            univ_sym  = o.get('universal_symbol') or {}
            is_option = bool(opt_sym)

            if is_option:
                ticker      = (opt_sym.get('underlying_symbol') or {}).get('symbol') or ''
                option_type = opt_sym.get('option_type', '').upper()
                strike      = opt_sym.get('strike_price')
                expiry      = opt_sym.get('expiration_date', '')[:10] if opt_sym.get('expiration_date') else None
                occ_ticker  = opt_sym.get('ticker', '')
            else:
                ticker      = univ_sym.get('symbol') or univ_sym.get('raw_symbol') or ''
                option_type = ''
                strike      = None
                expiry      = None
                occ_ticker  = ticker

            # Clean action: BUY_OPEN → BUY, SELL_TO_CLOSE → SELL
            raw_action = o.get('action', '')
            action = raw_action.replace('_OPEN','').replace('_TO_CLOSE','').replace('_CLOSE','').replace('_TO_OPEN','')

            fill_px  = float(o.get('execution_price') or 0) or None
            limit_px = float(o.get('limit_price') or 0) or None

            orders.append({
                'broker_order_id': o.get('brokerage_order_id'),
                'ticker': ticker,
                'occ_ticker': occ_ticker,
                'action': action,
                'is_option': is_option,
                'option_type': option_type,
                'strike': strike,
                'expiry': expiry,
                'total_quantity': float(o.get('total_quantity') or 0),
                'filled_quantity': float(o.get('filled_quantity') or 0),
                'open_quantity': float(o.get('open_quantity') or 0),
                'status': o.get('status', ''),
                'order_type': o.get('order_type', ''),
                'time_in_force': o.get('time_in_force', ''),
                'limit_price': limit_px,
                'fill_price': fill_px,
                'placed_at': o.get('time_placed'),
                'filled_at': o.get('time_executed'),
            })
        # Sort: pending first, then by placed_at desc
        status_rank = {'ACCEPTED': 0, 'PENDING': 0, 'PARTIALLY_FILLED': 1, 'EXECUTED': 2, 'EXPIRED': 3, 'CANCELED': 4}
        orders.sort(key=lambda x: (status_rank.get(x['status'], 5), -(0 if not x['placed_at'] else 1)))
        return Response(orders)


IBKR_SERVICE_URL = "http://127.0.0.1:8811"


class OptionsDomView(APIView):
    """Option-contract Depth of Market (Level 2) — proxied to the local
    IBKR microservice (ibkr_service.py), which holds the IB Gateway
    connection. Publisher-only by design (IBKR per-user data licensing).

    GET /api/brokers/dom/<ticker>/?expiry=YYYY-MM-DD&strike=300&right=C
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticker):
        params = {
            "ticker": ticker,
            "expiry": request.query_params.get("expiry", ""),
            "strike": request.query_params.get("strike", ""),
            "right": request.query_params.get("right", "C"),
        }
        try:
            resp = requests.get(f"{IBKR_SERVICE_URL}/dom", params=params, timeout=10)
            return Response(resp.json(), status=resp.status_code)
        except Exception as exc:
            logger.warning("IBKR DOM service unavailable | error=%s", exc)
            return Response(
                {"error": "IBKR depth service is offline — gateway may be down.",
                 "detail": str(exc)[:200]},
                status=503,
            )


class AccountSummaryView(APIView):
    """Aggregate stats for the connected-broker ribbon: balance, P&L, positions, followers."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from decimal import Decimal
        from django.db.models import Sum, Count
        from execution.models import Order
        from signals.models import CopyRelationship

        user = request.user
        today = timezone.now().date()

        conn = BrokerConnection.objects.filter(user=user, status="connected").first()
        if not conn:
            return Response({"connected": False})

        # Refresh buying power live from SnapTrade on each page load (self-healing account_id)
        if conn.broker == "snaptrade" and conn.snaptrade_user_id:
            try:
                balances = None
                if conn.account_id:
                    try:
                        balances = st.get_account_balances(conn.snaptrade_user_id, conn.snaptrade_user_secret, conn.account_id)
                    except Exception:
                        balances = None  # stale account_id, re-resolve below
                if balances is None:
                    accounts = st.get_accounts(conn.snaptrade_user_id, conn.snaptrade_user_secret)
                    if accounts:
                        acc = accounts[0].get("account", accounts[0])
                        new_id = acc.get("id", "")
                        if new_id and new_id != conn.account_id:
                            conn.account_id = new_id
                            logger.info("SnapTrade account_id re-resolved | user_id=%s account_id=%s", user.id, new_id)
                        if new_id:
                            balances = st.get_account_balances(conn.snaptrade_user_id, conn.snaptrade_user_secret, new_id)
                if balances:
                    cash = next((b for b in balances if b.get("currency", {}).get("code") == "USD"), None)
                    if cash:
                        conn.buying_power = cash.get("buying_power") or cash.get("cash", 0)
                    conn.last_synced = timezone.now()
                    conn.save(update_fields=["buying_power", "account_id", "last_synced"])
                    logger.info("Account balance refreshed from SnapTrade | user_id=%s buying_power=%s", user.id, conn.buying_power)
            except Exception as exc:
                logger.warning("Account balance refresh failed | user_id=%s reason=%s", user.id, exc)

        total_balance = float(conn.buying_power or 0)

        # Rough P&L: filled SELL value minus filled BUY value for today
        todays_orders = Order.objects.filter(user=user, filled_at__date=today, fill_price__isnull=False)
        sells = todays_orders.filter(direction="SELL").aggregate(
            v=Sum("fill_price"), q=Sum("quantity")
        )
        buys = todays_orders.filter(direction="BUY").aggregate(
            v=Sum("fill_price"), q=Sum("quantity")
        )
        sell_value = float((sells["v"] or 0) * (sells["q"] or 0) / max(todays_orders.filter(direction="SELL").count(), 1)) if sells["v"] else 0
        buy_value = float((buys["v"] or 0) * (buys["q"] or 0) / max(todays_orders.filter(direction="BUY").count(), 1)) if buys["v"] else 0
        pnl_today = round(sell_value - buy_value, 2)
        pnl_today_pct = round((pnl_today / total_balance * 100), 2) if total_balance else 0

        # Open positions = distinct tickers with submitted/filled orders not yet closed
        open_positions = (
            Order.objects.filter(user=user, status__in=["submitted", "filled"])
            .values("ticker")
            .distinct()
            .count()
        )

        # Followers (only if user is a trader)
        followers_count = 0
        try:
            trader = user.trader_profile
            followers_count = CopyRelationship.objects.filter(trader=trader, is_active=True).count()
        except Exception:
            pass

        return Response({
            "connected": True,
            "broker_name": conn.snaptrade_brokerage_name or conn.broker,
            "total_balance": total_balance,
            "pnl_today": pnl_today,
            "pnl_today_pct": pnl_today_pct,
            "open_positions": open_positions,
            "followers_count": followers_count,
            "last_synced": conn.last_synced.isoformat() if conn.last_synced else None,
        })
