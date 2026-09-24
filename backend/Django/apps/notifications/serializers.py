"""
Serializers for Notifications module.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'notif_id', 'user', 'username', 'title', 'message',
            'type', 'is_read', 'created_at'
        ]
        read_only_fields = ['notif_id', 'created_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications.
    """
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Notification
        fields = ['user_id', 'title', 'message', 'type', 'is_read']
    
    def create(self, validated_data):
        from apps.authentication.models import User
        user_id = validated_data.pop('user_id')
        user = User.objects.get(user_id=user_id)
        return Notification.objects.create(user=user, **validated_data)
