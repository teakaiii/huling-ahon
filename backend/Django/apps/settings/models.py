"""
Settings models for system configuration.
"""
from django.db import models
from apps.authentication.models import User
import uuid


class SystemSetting(models.Model):
    """
    Model to store system configuration settings.
    """
    setting_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_settings')
    
    class Meta:
        db_table = 'settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        indexes = [
            models.Index(fields=['key']),
        ]
    
    def __str__(self):
        return f"{self.key} = {self.value}"
