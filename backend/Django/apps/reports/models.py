"""
Reports models for managing generated reports.
"""
from django.db import models
from apps.authentication.models import User
import uuid


class Report(models.Model):
    """
    Model to store generated report metadata.
    """
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]
    
    FILE_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    start_date = models.DateField()
    end_date = models.DateField()
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_format = models.CharField(max_length=10, choices=FILE_FORMAT_CHOICES, blank=True, null=True)
    record_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['generated_by']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} Report ({self.start_date} to {self.end_date})"
