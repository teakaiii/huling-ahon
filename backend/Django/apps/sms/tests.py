"""
Unit tests for SMS module.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import SMSLog
from apps.water_level.models import WaterLevelReading
from apps.alerts.models import FloodAlert
from apps.residents.models import Resident
from apps.authentication.models import User


class SMSLogModelTest(TestCase):
    """Test cases for SMSLog model."""
    
    def setUp(self):
        self.resident = Resident.objects.create(
            full_name='John Doe',
            mobile_number='+639123456789',
            address='123 Test St',
            purok_zone='Zone 1'
        )
        self.reading = WaterLevelReading.objects.create(
            water_level_cm=70,
            status='Warning',
            timestamp=timezone.now()
        )
        self.alert = FloodAlert.objects.create(
            reading=self.reading,
            alert_level='Warning',
            message='Warning flood level detected',
            timestamp=timezone.now()
        )
        self.sms_log = SMSLog.objects.create(
            alert=self.alert,
            resident=self.resident,
            recipient='+639123456789',
            message='Test SMS message',
            delivery_status='delivered'
        )
    
    def test_sms_log_creation(self):
        """Test SMS log creation."""
        self.assertEqual(self.sms_log.recipient, '+639123456789')
        self.assertEqual(self.sms_log.delivery_status, 'delivered')
        self.assertEqual(self.sms_log.resident, self.resident)
        self.assertEqual(self.sms_log.alert, self.alert)
    
    def test_sms_log_str(self):
        """Test SMS log string representation."""
        str_repr = str(self.sms_log)
        self.assertIn('+639123456789', str_repr)
    
    def test_delivery_status_options(self):
        """Test delivery status options."""
        valid_statuses = ['pending', 'sent', 'delivered', 'failed']
        for status_option in valid_statuses:
            sms = SMSLog.objects.create(
                recipient='+639123456789',
                message='Test',
                delivery_status=status_option
            )
            self.assertEqual(sms.delivery_status, status_option)


class SMSAPITest(TestCase):
    """Test cases for SMS API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='staff'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        
        # Create test data
        self.resident = Resident.objects.create(
            full_name='Test Resident',
            mobile_number='+639123456789',
            address='Test Address',
            purok_zone='Zone 1'
        )
        
        for i in range(3):
            SMSLog.objects.create(
                recipient='+639123456789',
                resident=self.resident,
                message=f'Test SMS {i}',
                delivery_status=['delivered', 'sent', 'failed'][i]
            )
    
    def test_list_sms_logs_unauthorized(self):
        """Test list SMS logs without authentication."""
        response = self.client.get('/api/sms/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_sms_logs_authorized(self):
        """Test list SMS logs with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/sms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_sms_log_admin_only(self):
        """Test create SMS log requires admin."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/sms/create/', {
            'recipient': '+639123456789',
            'message': 'Test SMS'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_sms_log_admin_success(self):
        """Test create SMS log by admin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/sms/create/', {
            'recipient': '+639123456789',
            'message': 'Test SMS'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_statistics(self):
        """Test SMS statistics."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/sms/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_sent', response.data)
        self.assertIn('status_counts', response.data)
    
    def test_failed_sms(self):
        """Test get failed SMS logs."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/sms/failed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
