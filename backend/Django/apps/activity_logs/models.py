"""
Activity Logs models for audit trail.
"""
from django.db import models
from apps.authentication.models import User
import uuid


class ActivityLog(models.Model):
    """
    Model to track system activities for audit purposes.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('change_password', 'Change Password'),
        ('export', 'Export'),
        ('view', 'View'),
    ]
    
    ENTITY_CHOICES = [
        ('user', 'User'),
        ('barangay_staff', 'Barangay Staff'),
        ('resident', 'Resident'),
        ('water_level_reading', 'Water Level Reading'),
        ('flood_alert', 'Flood Alert'),
        ('sms_log', 'SMS Log'),
        ('prediction', 'Prediction'),
        ('report', 'Report'),
        ('setting', 'Setting'),
    ]
    
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity = models.CharField(max_length=50, choices=ENTITY_CHOICES)
    entity_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.action} {self.entity} at {self.timestamp}"
