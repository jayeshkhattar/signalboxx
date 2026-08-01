from django.urls import path
from .views import (
    SchwabConnectView, SchwabCallbackView, WebullConnectView,
    BrokerConnectionListView, BrokerConnectionDetailView, BrokerSyncView,
    SnapTradeConnectView, SnapTradeCallbackView, SnapTradeDisconnectView,
    QuoteView, AccountSummaryView, OptionsChainView, OptionsDomView,
    BrokerPositionsView, BrokerOrdersView,
)
urlpatterns = [
    path("connect/schwab/", SchwabConnectView.as_view(), name="schwab-connect"),
    path("callback/schwab/", SchwabCallbackView.as_view(), name="schwab-callback"),
    path("connect/webull/", WebullConnectView.as_view(), name="webull-connect"),
    path("connect/snaptrade/", SnapTradeConnectView.as_view(), name="snaptrade-connect"),
    path("callback/snaptrade/", SnapTradeCallbackView.as_view(), name="snaptrade-callback"),
    path("disconnect/snaptrade/", SnapTradeDisconnectView.as_view(), name="snaptrade-disconnect"),
    path("connections/", BrokerConnectionListView.as_view(), name="broker-connections"),
    path("connections/<int:pk>/", BrokerConnectionDetailView.as_view(), name="broker-connection-detail"),
    path("connections/<int:pk>/sync/", BrokerSyncView.as_view(), name="broker-sync"),
    path("quote/<str:ticker>/", QuoteView.as_view(), name="quote"),
    path("options-chain/<str:ticker>/", OptionsChainView.as_view(), name="options-chain"),
    path("dom/<str:ticker>/", OptionsDomView.as_view(), name="options-dom"),
    path("account-summary/", AccountSummaryView.as_view(), name="account-summary"),
    path("live-positions/", BrokerPositionsView.as_view(), name="broker-live-positions"),
    path("live-orders/", BrokerOrdersView.as_view(), name="broker-live-orders"),
]
