"""
Serializers for SMS Logs module.
"""
from rest_framework import serializers
from .models import SMSLog


class SMSLogSerializer(serializers.ModelSerializer):
    """
    Serializer for SMSLog model.
    """
    resident_name = serializers.CharField(source='resident.full_name', read_only=True)
    resident_purok = serializers.CharField(source='resident.purok_zone', read_only=True)
    alert_level = serializers.CharField(source='alert.alert_level', read_only=True, allow_null=True)
    
    class Meta:
        model = SMSLog
        fields = [
            'sms_id', 'alert', 'resident', 'recipient', 'message',
            'sent_at', 'delivery_status', 'error_message',
            'resident_name', 'resident_purok', 'alert_level'
        ]
        read_only_fields = ['sms_id', 'sent_at']


class SMSLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating SMS logs.
    """
    alert_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    resident_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = SMSLog
        fields = ['alert_id', 'resident_id', 'recipient', 'message', 'delivery_status', 'error_message']
    
    def create(self, validated_data):
        from apps.alerts.models import FloodAlert
        from apps.residents.models import Resident
        
        alert_id = validated_data.pop('alert_id', None)
        resident_id = validated_data.pop('resident_id')
        
        resident = Resident.objects.get(resident_id=resident_id)
        alert = FloodAlert.objects.get(alert_id=alert_id) if alert_id else None
        
        return SMSLog.objects.create(alert=alert, resident=resident, **validated_data)
