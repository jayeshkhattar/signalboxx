# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/analytics/urls.py
# Compiled at: 2026-05-08 16:25:29
# Size of source mod 2**32: 254 bytes
from django.urls import path
from .views import PerformanceView, TraderAnalyticsView, PnLCalendarView
urlpatterns = [
 path("performance/", (PerformanceView.as_view()), name="performance"),
 path("trader/", (TraderAnalyticsView.as_view()), name="trader-analytics"),
 path("calendar/", (PnLCalendarView.as_view()), name="pnl-calendar")]

# okay decompiling ./analytics/__pycache__/urls.cpython-37.pyc
