"""
Serializers for Activity Logs module.
"""
from rest_framework import serializers
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ActivityLog model.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'log_id', 'user', 'username', 'user_role', 'action', 'entity',
            'entity_id', 'details', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['log_id', 'timestamp']
