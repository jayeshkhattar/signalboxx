# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signalboxx/urls.py
# Compiled at: 2026-05-09 20:55:20
# Size of source mod 2**32: 3337 bytes
import logging, threading
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
auth_logger = logging.getLogger("signalboxx.auth")

def _background_snaptrade_sync(user_id: int) -> None:
    """Run SnapTrade sync in a daemon thread so login latency is unaffected."""
    try:
        from users.models import User
        from brokers.sync import sync_all_snaptrade_for_user
        user = User.objects.get(id=user_id)
        sync_all_snaptrade_for_user(user)
    except Exception as exc:
        try:
            auth_logger.warning("Background SnapTrade sync failed | user_id=%s reason=%s", user_id, exc)
        finally:
            exc = None
            del exc


class LoggedTokenObtainPairView(TokenObtainPairView):
    __doc__ = "JWT login — logs success/failure and triggers a SnapTrade sync in the background."

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "—")
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "—"))
        auth_logger.debug("Login attempt | email=%s ip=%s", email, ip)
        response = (super().post)(request, *args, **kwargs)
        if response.status_code == 200:
            auth_logger.info("Login success | email=%s ip=%s", email, ip)
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                token_str = response.data.get("access", "")
                user_id = AccessToken(token_str).get("user_id")
                if user_id:
                    t = threading.Thread(target=_background_snaptrade_sync,
                      args=(
                     user_id,),
                      daemon=True,
                      name=f"snaptrade-sync-{user_id}")
                    t.start()
                    auth_logger.debug("SnapTrade sync thread started | user_id=%s", user_id)
            except Exception as exc:
                try:
                    auth_logger.warning("Could not start SnapTrade sync thread | reason=%s", exc)
                finally:
                    exc = None
                    del exc

        else:
            auth_logger.warning("Login failed | email=%s ip=%s status=%s", email, ip, response.status_code)
        return response


class LoggedTokenRefreshView(TokenRefreshView):
    __doc__ = "JWT refresh — logs each refresh event."

    def post(self, request, *args, **kwargs):
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "—"))
        response = (super().post)(request, *args, **kwargs)
        if response.status_code == 200:
            auth_logger.debug("Token refreshed | ip=%s", ip)
        else:
            auth_logger.warning("Token refresh failed | ip=%s status=%s", ip, response.status_code)
        return response


urlpatterns = [
 path("", TemplateView.as_view(template_name="index.html"), name="home"),
 path("api/auth/token/", (LoggedTokenObtainPairView.as_view()), name="token_obtain_pair"),
 path("api/auth/token/refresh/", (LoggedTokenRefreshView.as_view()), name="token_refresh"),
 path("api/users/", include("users.urls")),
 path("api/brokers/", include("brokers.urls")),
 path("api/", include("signals.urls")),
 path("api/", include("execution.urls")),
 path("api/analytics/", include("analytics.urls"))]

# okay decompiling ./signalboxx/__pycache__/urls.cpython-37.pyc
