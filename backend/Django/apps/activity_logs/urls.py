"""
URL configuration for Activity Logs module.
"""
from django.urls import path
from .views import ActivityLogListView, ActivityLogDetailView

urlpatterns = [
    path('', ActivityLogListView.as_view(), name='activity_log_list'),
    path('<uuid:log_id>/', ActivityLogDetailView.as_view(), name='activity_log_detail'),
]
