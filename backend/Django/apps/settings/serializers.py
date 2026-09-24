"""
Serializers for Settings module.
"""
from rest_framework import serializers
from .models import SystemSetting


class SystemSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for SystemSetting model.
    """
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = SystemSetting
        fields = [
            'setting_id', 'key', 'value', 'description',
            'updated_at', 'updated_by', 'updated_by_username'
        ]
        read_only_fields = ['setting_id', 'updated_at']


class SystemSettingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating system settings.
    """
    class Meta:
        model = SystemSetting
        fields = ['key', 'value', 'description']
