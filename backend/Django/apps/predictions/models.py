"""
AI Prediction models for flood prediction results.
"""
from django.db import models
from apps.water_level.models import WaterLevelReading
import uuid


class Prediction(models.Model):
    """
    Model to store AI flood prediction results.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_LEVEL_CHOICES = [
        ('Normal', 'Normal'),
        ('Alert', 'Alert'),
        ('Warning', 'Warning'),
        ('Danger', 'Danger'),
    ]
    
    prediction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reading = models.ForeignKey(WaterLevelReading, on_delete=models.CASCADE, related_name='predictions')
    flood_probability = models.DecimalField(max_digits=5, decimal_places=2)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVEL_CHOICES)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    recommended_action = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'predictions'
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['severity']),
            models.Index(fields=['alert_level']),
            models.Index(fields=['reading']),
        ]
    
    def __str__(self):
        return f"{self.severity} severity - {self.flood_probability}% probability at {self.timestamp}"


class AIModel(models.Model):
    """
    Model to store AI model information and versions.
    """
    MODEL_TYPE_CHOICES = [
        ('random_forest', 'Random Forest'),
        ('decision_tree', 'Decision Tree'),
        ('logistic_regression', 'Logistic Regression'),
    ]
    
    model_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES)
    version = models.CharField(max_length=20)
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    precision = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    trained_at = models.DateTimeField(null=True, blank=True)
    model_file_path = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_models'
        verbose_name = 'AI Model'
        verbose_name_plural = 'AI Models'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name']),
            models.Index(fields=['model_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['trained_at']),
        ]
    
    def __str__(self):
        return f"{self.model_name} v{self.version} ({self.get_model_type_display()})"
