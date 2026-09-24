"""
URL configuration for Notifications module.
"""
from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    NotificationCreateView,
    mark_all_read_view,
    unread_count_view
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('<uuid:notif_id>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('create/', NotificationCreateView.as_view(), name='notification_create'),
    path('mark-all-read/', mark_all_read_view, name='mark_all_read'),
    path('unread-count/', unread_count_view, name='unread_count'),
]
