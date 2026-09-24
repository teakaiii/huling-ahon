"""
URL configuration for Flood Alerts module.
"""
from django.urls import path
from .views import (
    FloodAlertListView,
    FloodAlertDetailView,
    FloodAlertCreateView,
    send_manual_warning_view,
    active_alerts_view,
    recent_alerts_view,
    alert_statistics_view
)

urlpatterns = [
    path('', FloodAlertListView.as_view(), name='alert_list'),
    path('manual-warning/', send_manual_warning_view, name='manual_warning'),
    path('<uuid:alert_id>/', FloodAlertDetailView.as_view(), name='alert_detail'),
    path('create/', FloodAlertCreateView.as_view(), name='alert_create'),
    path('active/', active_alerts_view, name='active_alerts'),
    path('recent/', recent_alerts_view, name='recent_alerts'),
    path('statistics/', alert_statistics_view, name='alert_statistics'),
]
