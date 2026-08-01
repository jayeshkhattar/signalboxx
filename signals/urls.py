# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/signals/urls.py
# Compiled at: 2026-05-08 17:31:31
# Size of source mod 2**32: 1046 bytes
from django.urls import path
from .views import TraderListView, FollowTraderView, SignalFeedView, TraderRegisterView, TraderMeView, TraderFollowersView, TraderMySignalsView, PostSignalView, MyRelationshipsView
urlpatterns = [
 path("traders/", (TraderListView.as_view()), name="trader-list"),
 path("traders/<int:trader_id>/follow/", (FollowTraderView.as_view()), name="trader-follow"),
 path("signals/", (SignalFeedView.as_view()), name="signal-feed"),
 path("traders/register/", (TraderRegisterView.as_view()), name="trader-register"),
 path("traders/me/", (TraderMeView.as_view()), name="trader-me"),
 path("traders/me/followers/", (TraderFollowersView.as_view()), name="trader-followers"),
 path("traders/me/signals/", (TraderMySignalsView.as_view()), name="trader-my-signals"),
 path("signals/post/", (PostSignalView.as_view()), name="signal-post"),
 path("traders/relationships/", (MyRelationshipsView.as_view()), name="my-relationships")]

# okay decompiling ./signals/__pycache__/urls.cpython-37.pyc
