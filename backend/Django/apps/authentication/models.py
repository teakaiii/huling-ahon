"""
Authentication models for User and BarangayStaff.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Barangay Staff'),
    ]
    
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_staff_user(self):
        return self.role == 'staff'


class BarangayStaff(models.Model):
    """
    Extended profile for Barangay Staff members.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    staff_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    purok_zone = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'barangay_staff'
        verbose_name = 'Barangay Staff'
        verbose_name_plural = 'Barangay Staff'
    
    def __str__(self):
        return f"{self.full_name} - {self.purok_zone or 'Unassigned'}"
