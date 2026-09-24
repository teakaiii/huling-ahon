"""
Views for Activity Logs module.
"""
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogListView(generics.ListAPIView):
    """
    API endpoint to list all activity logs.
    Only admins can access this endpoint.
    """
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'entity', 'user']
    search_fields = ['user__username', 'entity', 'action']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']


class ActivityLogDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a specific activity log.
    Only admins can access this endpoint.
    """
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    lookup_field = 'log_id'
