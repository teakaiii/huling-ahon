"""
Views for Notifications module.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer
)


class NotificationListView(generics.ListAPIView):
    """
    API endpoint to list all notifications for the current user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'notif_id'
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='notification',
            entity_id=str(self.get_object().notif_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='notification',
            entity_id=str(instance.notif_id),
            details={'title': instance.title}
        )
        instance.delete()


class NotificationCreateView(generics.CreateAPIView):
    """
    API endpoint to create a notification.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='notification',
            details=serializer.validated_data
        )
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read_view(request):
    """
    API endpoint to mark all notifications as read for the current user.
    """
    updated_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Log activity
    from apps.activity_logs.utils import log_activity
    log_activity(
        user=request.user,
        action='mark_all_read',
        entity='notification',
        details={'count': updated_count}
    )
    
    return Response({
        'message': f'{updated_count} notifications marked as read.',
        'count': updated_count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count_view(request):
    """
    API endpoint to get the count of unread notifications for the current user.
    """
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})
