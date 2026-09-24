"""
Residents models for managing resident information.
"""
from django.db import models
import uuid


class Resident(models.Model):
    """
    Model to store resident information for SMS alerts.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('evacuated', 'Evacuated'),
    ]
    
    resident_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    purok_zone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    sms_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'residents'
        verbose_name = 'Resident'
        verbose_name_plural = 'Residents'
        ordering = ['purok_zone', 'full_name']
        indexes = [
            models.Index(fields=['mobile_number']),
            models.Index(fields=['purok_zone']),
            models.Index(fields=['status']),
            models.Index(fields=['sms_enabled']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.purok_zone} ({self.mobile_number})"
    
    def validate_mobile_number(self):
        """
        Validate mobile number format.
        """
        if not self.mobile_number.startswith('+63'):
            raise ValueError("Mobile number must start with +63")
        if len(self.mobile_number) != 13:
            raise ValueError("Mobile number must be 13 characters (e.g., +639123456789)")
