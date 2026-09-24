"""
Flood Alerts models for managing flood alert events.
"""
from django.db import models
from apps.water_level.models import WaterLevelReading
import uuid


class FloodAlert(models.Model):
    """
    Model to store flood alert events.
    """
    ALERT_LEVEL_CHOICES = [
        ('Alert', 'Alert'),
        ('Warning', 'Warning'),
        ('Danger', 'Danger'),
    ]
    
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reading = models.ForeignKey(WaterLevelReading, on_delete=models.CASCADE, related_name='alerts')
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVEL_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'flood_alerts'
        verbose_name = 'Flood Alert'
        verbose_name_plural = 'Flood Alerts'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['alert_level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['reading']),
        ]
    
    def __str__(self):
        return f"{self.alert_level} Alert at {self.timestamp}"
