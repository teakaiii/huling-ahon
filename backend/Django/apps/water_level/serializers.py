"""
Serializers for Water Level module.
"""
from rest_framework import serializers
from .models import WaterLevelReading


class WaterLevelReadingSerializer(serializers.ModelSerializer):
    """
    Serializer for WaterLevelReading model.
    """
    class Meta:
        model = WaterLevelReading
        fields = [
            'reading_id', 'water_level_cm', 'status', 'timestamp',
            'sensor_status', 'gsm_status', 'firebase_synced', 'created_at'
        ]
        read_only_fields = ['reading_id', 'created_at']


class WaterLevelReadingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating water level readings (used by Firebase sync).
    """
    class Meta:
        model = WaterLevelReading
        fields = [
            'water_level_cm', 'status', 'timestamp',
            'sensor_status', 'gsm_status'
        ]
    
    def create(self, validated_data):
        # Auto-determine status if not provided
        if 'status' not in validated_data:
            from django.conf import settings
            water_level = validated_data['water_level_cm']
            validated_data['status'] = WaterLevelReading.get_flood_status(water_level)
        
        return WaterLevelReading.objects.create(**validated_data)


class CurrentWaterLevelSerializer(serializers.Serializer):
    """
    Serializer for current water level data.
    """
    reading_id = serializers.UUIDField()
    water_level_cm = serializers.DecimalField(max_digits=5, decimal_places=2)
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    sensor_status = serializers.CharField()
    gsm_status = serializers.CharField()
    firebase_synced = serializers.BooleanField()
