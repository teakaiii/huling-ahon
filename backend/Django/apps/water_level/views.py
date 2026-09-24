"""
Views for Water Level module.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from .models import WaterLevelReading
from .serializers import (
    WaterLevelReadingSerializer,
    WaterLevelReadingCreateSerializer,
    CurrentWaterLevelSerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def public_water_level_ingest_view(request):
    """
    Public endpoint for Arduino or edge devices to send flood readings without JWT.
    Accepts both the project-standard field name `water_level_cm` and legacy alias
    `water_level` used by older hardware payloads.
    """
    try:
        payload = request.data.copy()

        raw_water_level = payload.get('water_level_cm', payload.get('water_level'))
        if raw_water_level is None or raw_water_level == '':
            return Response(
                {'error': 'water_level_cm or water_level is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            water_level = Decimal(str(raw_water_level))
        except InvalidOperation:
            return Response(
                {'error': 'water_level must be numeric.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sensor_status = payload.get('sensor_status', 'online')
        gsm_status = payload.get('gsm_status', 'connected')
        status_value = payload.get('status') or WaterLevelReading.get_flood_status(water_level)

        timestamp_value = payload.get('timestamp')
        if timestamp_value:
            try:
                timestamp = datetime.fromisoformat(str(timestamp_value).replace('Z', '+00:00'))
                if timezone.is_naive(timestamp):
                    timestamp = timezone.make_aware(timestamp, timezone.utc)
                else:
                    timestamp = timestamp.astimezone(timezone.utc)
            except ValueError:
                timestamp = timezone.now()
        else:
            timestamp = timezone.now()

        reading = WaterLevelReading.objects.create(
            water_level_cm=water_level,
            status=status_value,
            timestamp=timestamp,
            sensor_status=sensor_status,
            gsm_status=gsm_status,
            firebase_synced=False,
        )

        serializer = WaterLevelReadingSerializer(reading)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class WaterLevelReadingListView(generics.ListAPIView):
    """
    API endpoint to list all water level readings.
    """
    queryset = WaterLevelReading.objects.all()
    serializer_class = WaterLevelReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'sensor_status', 'gsm_status']
    search_fields = ['status']
    ordering_fields = ['timestamp', 'water_level_cm']
    ordering = ['-timestamp']


class WaterLevelReadingDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a specific water level reading.
    """
    queryset = WaterLevelReading.objects.all()
    serializer_class = WaterLevelReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'reading_id'


class WaterLevelReadingCreateView(generics.CreateAPIView):
    """
    API endpoint to create water level readings.
    Used by Firebase sync service.
    """
    queryset = WaterLevelReading.objects.all()
    serializer_class = WaterLevelReadingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='water_level_reading',
            details=serializer.validated_data
        )
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_water_level_view(request):
    """
    API endpoint to get the current water level reading from the sensor feed.
    """
    try:
        # Read Firebase first so the dashboard reflects the latest Arduino upload.
        try:
            from backend.api.firebase_service import firebase_service

            firebase_data = firebase_service.get_current_water_level()
            if firebase_data:
                synced_reading = firebase_service.sync_water_level_to_postgres(firebase_data)
                if synced_reading:
                    serializer = CurrentWaterLevelSerializer(synced_reading)
                    response_data = serializer.data
                    response_data['source'] = 'firebase_sensor'
                    return Response(response_data)
        except Exception as firebase_error:
            import logging
            logging.getLogger(__name__).warning(
                'Live Firebase reading unavailable: %s', firebase_error
            )

        reading = WaterLevelReading.objects.order_by('-timestamp').first()
        
        if not reading:
            # Create sample reading if none exists
            reading = WaterLevelReading.objects.create(
                water_level_cm=15.5,
                status='Normal',
                sensor_status='online',
                gsm_status='connected'
            )
        
        serializer = CurrentWaterLevelSerializer(reading)
        response_data = serializer.data
        response_data['source'] = 'database'
        return Response(response_data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def water_level_history_view(request):
    """
    API endpoint to get water level history for a specific time range.
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    try:
        hours = request.query_params.get('hours', 24)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = WaterLevelReading.objects.all()
        
        if start_date and end_date:
            # Filter by date range
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            queryset = queryset.filter(timestamp__gte=start_datetime, timestamp__lt=end_datetime)
        else:
            # Filter by hours
            cutoff_time = timezone.now() - timedelta(hours=int(hours))
            queryset = queryset.filter(timestamp__gte=cutoff_time)
        
        readings = queryset.order_by('timestamp')
        
        # If no data exists, generate sample historical data
        if not readings.exists():
            import random
            from datetime import timedelta
            base_time = timezone.now() - timedelta(hours=int(hours))
            for i in range(int(hours)):
                reading = WaterLevelReading.objects.create(
                    water_level_cm=round(random.uniform(10, 20), 1),
                    status='Normal' if random.random() > 0.3 else 'Alert',
                    sensor_status='online',
                    gsm_status='connected',
                    timestamp=base_time + timedelta(hours=i)
                )
            readings = WaterLevelReading.objects.filter(timestamp__gte=cutoff_time).order_by('timestamp')
        
        serializer = WaterLevelReadingSerializer(readings, many=True)
        
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def water_level_statistics_view(request):
    """
    API endpoint to get water level statistics.
    Query parameters:
    - hours: Number of hours to look back (default: 24)
    """
    try:
        hours = request.query_params.get('hours', 24)
        cutoff_time = timezone.now() - timedelta(hours=int(hours))
        
        readings = WaterLevelReading.objects.filter(timestamp__gte=cutoff_time)
        
        if not readings.exists():
            return Response(
                {'message': 'No data available for the specified time range.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        stats = readings.aggregate(
            avg_level=models.Avg('water_level_cm'),
            max_level=models.Max('water_level_cm'),
            min_level=models.Min('water_level_cm'),
            count=models.Count('reading_id')
        )
        
        # Count by status
        status_counts = {}
        for status_choice in WaterLevelReading.STATUS_CHOICES:
            status_name = status_choice[0]
            count = readings.filter(status=status_name).count()
            status_counts[status_name] = count
        
        data = {
            'average_level': round(float(stats['avg_level']), 2) if stats['avg_level'] else 0,
            'max_level': float(stats['max_level']) if stats['max_level'] else 0,
            'min_level': float(stats['min_level']) if stats['min_level'] else 0,
            'total_readings': stats['count'],
            'status_counts': status_counts,
            'time_range_hours': int(hours)
        }
        
        return Response(data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
