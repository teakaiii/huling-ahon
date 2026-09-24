"""
URL configuration for SMS Logs module.
"""
from django.urls import path
from .views import (
    SMSLogListView,
    SMSLogDetailView,
    SMSLogCreateView,
    sms_statistics_view,
    failed_sms_view
)

urlpatterns = [
    path('', SMSLogListView.as_view(), name='sms_log_list'),
    path('<uuid:sms_id>/', SMSLogDetailView.as_view(), name='sms_log_detail'),
    path('create/', SMSLogCreateView.as_view(), name='sms_log_create'),
    path('statistics/', sms_statistics_view, name='sms_statistics'),
    path('failed/', failed_sms_view, name='failed_sms'),
]
