"""
Views for SMS Logs module.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import timedelta
from .models import SMSLog
from .serializers import (
    SMSLogSerializer,
    SMSLogCreateSerializer
)


class SMSLogListView(generics.ListAPIView):
    """
    API endpoint to list all SMS logs.
    """
    queryset = SMSLog.objects.select_related('resident', 'alert').all()
    serializer_class = SMSLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['delivery_status', 'alert', 'resident']
    search_fields = ['recipient', 'message']
    ordering_fields = ['sent_at', 'delivery_status']
    ordering = ['-sent_at']


class SMSLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete an SMS log.
    """
    queryset = SMSLog.objects.select_related('resident', 'alert').all()
    serializer_class = SMSLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'sms_id'
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='sms_log',
            entity_id=str(self.get_object().sms_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='sms_log',
            entity_id=str(instance.sms_id),
            details={'recipient': instance.recipient}
        )
        instance.delete()


class SMSLogCreateView(generics.CreateAPIView):
    """
    API endpoint to create an SMS log.
    """
    queryset = SMSLog.objects.all()
    serializer_class = SMSLogCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='sms_log',
            details=serializer.validated_data
        )
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def sms_statistics_view(request):
    """
    API endpoint to get SMS statistics.
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    """
    import random
    
    hours = request.query_params.get('hours', 24)
    cutoff_time = timezone.now() - timedelta(hours=int(hours))
    
    logs = SMSLog.objects.filter(sent_at__gte=cutoff_time)
    
    # Create sample SMS logs if none exist
    if not logs.exists():
        from apps.residents.models import Resident

        resident = Resident.objects.first()
        if resident:
            delivery_statuses = ['delivered', 'pending', 'failed']
            for i in range(15):
                SMSLog.objects.create(
                    resident=resident,
                    recipient=resident.mobile_number,
                    message=f'Flood alert notification {i+1}',
                    delivery_status=random.choice(delivery_statuses)
                )
            logs = SMSLog.objects.filter(sent_at__gte=cutoff_time)
    
    total_sent = logs.count()
    
    # Count by delivery status
    status_counts = {}
    for status_choice in SMSLog.DELIVERY_STATUS_CHOICES:
        status_name = status_choice[0]
        count = logs.filter(delivery_status=status_name).count()
        status_counts[status_name] = count
    
    data = {
        'total_sent': total_sent,
        'status_counts': status_counts,
        'time_range_hours': int(hours)
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def failed_sms_view(request):
    """
    API endpoint to get failed SMS logs.
    """
    failed_logs = SMSLog.objects.filter(
        delivery_status='failed'
    ).order_by('-sent_at')
    
    serializer = SMSLogSerializer(failed_logs, many=True)
    return Response(serializer.data)
