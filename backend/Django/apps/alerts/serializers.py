"""
Serializers for Flood Alerts module.
"""
from rest_framework import serializers
from .models import FloodAlert


class FloodAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for FloodAlert model.
    """
    water_level = serializers.DecimalField(source='reading.water_level_cm', read_only=True, max_digits=5, decimal_places=2)
    reading_timestamp = serializers.DateTimeField(source='reading.timestamp', read_only=True)
    
    class Meta:
        model = FloodAlert
        fields = [
            'alert_id', 'reading', 'water_level', 'reading_timestamp',
            'alert_level', 'message', 'timestamp', 'is_active', 'created_at'
        ]
        read_only_fields = ['alert_id', 'created_at']


class FloodAlertCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating flood alerts.
    """
    reading_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = FloodAlert
        fields = ['reading_id', 'alert_level', 'message', 'timestamp', 'is_active']
    
    def create(self, validated_data):
        from apps.water_level.models import WaterLevelReading
        reading_id = validated_data.pop('reading_id')
        reading = WaterLevelReading.objects.get(reading_id=reading_id)
        return FloodAlert.objects.create(reading=reading, **validated_data)
