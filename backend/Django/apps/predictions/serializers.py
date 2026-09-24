"""
Serializers for AI Predictions module.
"""
from rest_framework import serializers
from .models import Prediction, AIModel


class PredictionSerializer(serializers.ModelSerializer):
    """
    Serializer for Prediction model.
    """
    water_level = serializers.DecimalField(source='reading.water_level_cm', read_only=True, max_digits=5, decimal_places=2)
    reading_timestamp = serializers.DateTimeField(source='reading.timestamp', read_only=True)
    
    class Meta:
        model = Prediction
        fields = [
            'prediction_id', 'reading', 'water_level', 'reading_timestamp',
            'flood_probability', 'severity', 'alert_level', 'confidence_score',
            'recommended_action', 'timestamp', 'created_at'
        ]
        read_only_fields = ['prediction_id', 'created_at']


class PredictionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating predictions.
    """
    reading_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Prediction
        fields = [
            'reading_id', 'flood_probability', 'severity', 'alert_level',
            'confidence_score', 'recommended_action', 'timestamp'
        ]
    
    def create(self, validated_data):
        from apps.water_level.models import WaterLevelReading
        reading_id = validated_data.pop('reading_id')
        reading = WaterLevelReading.objects.get(reading_id=reading_id)
        return Prediction.objects.create(reading=reading, **validated_data)


class AIModelSerializer(serializers.ModelSerializer):
    """
    Serializer for AIModel model.
    """
    class Meta:
        model = AIModel
        fields = [
            'model_id', 'model_name', 'model_type', 'version',
            'accuracy', 'precision', 'recall', 'f1_score',
            'trained_at', 'model_file_path', 'is_active', 'created_at'
        ]
        read_only_fields = ['model_id', 'created_at']


class AIModelCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating AI models.
    """
    class Meta:
        model = AIModel
        fields = [
            'model_name', 'model_type', 'version',
            'accuracy', 'precision', 'recall', 'f1_score',
            'trained_at', 'model_file_path', 'is_active'
        ]
