from django.urls import path
from .views import OrderListView, OrderDetailView, OrderConfirmView, OrderCancelView, KillSwitchView, RiskSettingsView, OpenPositionsView, ExitPositionView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/positions/', OpenPositionsView.as_view(), name='open-positions'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/confirm/', OrderConfirmView.as_view(), name='order-confirm'),
    path('orders/<int:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('orders/<int:pk>/exit/', ExitPositionView.as_view(), name='exit-position'),
    path('risk/kill-switch/', KillSwitchView.as_view(), name='kill-switch'),
    path('risk/settings/', RiskSettingsView.as_view(), name='risk-settings'),
]
