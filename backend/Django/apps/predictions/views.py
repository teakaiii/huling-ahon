"""
Views for AI Predictions module.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import models
from datetime import timedelta
from .models import Prediction, AIModel
from .serializers import (
    PredictionSerializer,
    PredictionCreateSerializer,
    AIModelSerializer,
    AIModelCreateSerializer
)


class PredictionListView(generics.ListAPIView):
    """
    API endpoint to list all predictions.
    """
    queryset = Prediction.objects.select_related('reading').all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['severity', 'alert_level']
    search_fields = ['recommended_action', 'severity']
    ordering_fields = ['timestamp', 'flood_probability']
    ordering = ['-timestamp']


class PredictionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a prediction.
    """
    queryset = Prediction.objects.select_related('reading').all()
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'prediction_id'
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='prediction',
            entity_id=str(self.get_object().prediction_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='prediction',
            entity_id=str(instance.prediction_id),
            details={'severity': instance.severity}
        )
        instance.delete()


class PredictionCreateView(generics.CreateAPIView):
    """
    API endpoint to create a prediction.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='prediction',
            details=serializer.validated_data
        )
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def latest_prediction_view(request):
    """
    API endpoint to get the latest prediction.
    """
    try:
        prediction = Prediction.objects.order_by('-timestamp').first()
        
        if prediction:
            serializer = PredictionSerializer(prediction)
            return Response(serializer.data)
        else:
            return Response(
                {'message': 'No predictions available.'},
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def prediction_statistics_view(request):
    """
    API endpoint to get prediction statistics.
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    """
    hours = request.query_params.get('hours', 24)
    cutoff_time = timezone.now() - timedelta(hours=int(hours))
    
    predictions = Prediction.objects.filter(timestamp__gte=cutoff_time)
    
    if not predictions.exists():
        return Response(
            {'message': 'No prediction data available for the specified time range.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Average confidence score
    avg_confidence = predictions.aggregate(
        avg_confidence=models.Avg('confidence_score')
    )['avg_confidence']
    
    # Count by severity
    severity_counts = {}
    for severity_choice in Prediction.SEVERITY_CHOICES:
        severity_name = severity_choice[0]
        count = predictions.filter(severity=severity_name).count()
        severity_counts[severity_name] = count
    
    # Count by alert level
    alert_counts = {}
    for alert_choice in Prediction.ALERT_LEVEL_CHOICES:
        alert_name = alert_choice[0]
        count = predictions.filter(alert_level=alert_name).count()
        alert_counts[alert_name] = count
    
    data = {
        'total_predictions': predictions.count(),
        'average_confidence': round(float(avg_confidence), 2) if avg_confidence else 0,
        'severity_counts': severity_counts,
        'alert_counts': alert_counts,
        'time_range_hours': int(hours)
    }
    
    return Response(data)


# AI Model Views
class AIModelListView(generics.ListAPIView):
    """
    API endpoint to list all AI models.
    """
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['model_type', 'is_active']
    search_fields = ['model_name', 'version']
    ordering_fields = ['created_at', 'trained_at']
    ordering = ['-created_at']


class AIModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete an AI model.
    """
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'model_id'
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='ai_model',
            entity_id=str(self.get_object().model_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='ai_model',
            entity_id=str(instance.model_id),
            details={'model_name': instance.model_name}
        )
        instance.delete()


class AIModelCreateView(generics.CreateAPIView):
    """
    API endpoint to create an AI model.
    """
    queryset = AIModel.objects.all()
    serializer_class = AIModelCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='ai_model',
            details=serializer.validated_data
        )
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def active_model_view(request):
    """
    API endpoint to get the active AI model.
    """
    try:
        model = AIModel.objects.filter(is_active=True).first()
        
        if model:
            serializer = AIModelSerializer(model)
            return Response(serializer.data)
        else:
            return Response(
                {'message': 'No active AI model found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
