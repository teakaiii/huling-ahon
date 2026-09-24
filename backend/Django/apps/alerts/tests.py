"""
Unit tests for Alerts module.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import FloodAlert
from apps.water_level.models import WaterLevelReading
from apps.authentication.models import User


class FloodAlertModelTest(TestCase):
    """Test cases for FloodAlert model."""
    
    def setUp(self):
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
    
    def test_alert_creation(self):
        """Test alert creation."""
        self.assertEqual(self.alert.alert_level, 'Warning')
        self.assertEqual(self.alert.message, 'Warning flood level detected')
        self.assertTrue(self.alert.is_active)
    
    def test_alert_str(self):
        """Test alert string representation."""
        str_repr = str(self.alert)
        self.assertIn('Warning', str_repr)
    
    def test_alert_deactivation(self):
        """Test alert deactivation."""
        self.alert.is_active = False
        self.alert.save()
        self.assertFalse(self.alert.is_active)


class AlertsAPITest(TestCase):
    """Test cases for Alerts API endpoints."""
    
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
        
        # Create test readings and alerts
        for i in range(3):
            reading = WaterLevelReading.objects.create(
                water_level_cm=50 + i * 15,
                timestamp=timezone.now() - timezone.timedelta(hours=i)
            )
            FloodAlert.objects.create(
                reading=reading,
                alert_level=['Alert', 'Warning', 'Danger'][i],
                message=f'Test alert {i}',
                timestamp=timezone.now() - timezone.timedelta(hours=i)
            )
    
    def test_list_alerts_unauthorized(self):
        """Test list alerts without authentication."""
        response = self.client.get('/api/alerts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_alerts_authorized(self):
        """Test list alerts with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/alerts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_active_alerts(self):
        """Test get active alerts."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/alerts/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_alert_admin_only(self):
        """Test create alert requires admin."""
        self.client.force_authenticate(user=self.user)
        reading = WaterLevelReading.objects.first()
        response = self.client.post('/api/alerts/create/', {
            'reading_id': str(reading.reading_id),
            'alert_level': 'Warning',
            message='Test alert'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_alert_admin_success(self):
        """Test create alert by admin."""
        self.client.force_authenticate(user=self.admin_user)
        reading = WaterLevelReading.objects.first()
        response = self.client.post('/api/alerts/create/', {
            'reading_id': str(reading.reading_id),
            'alert_level': 'Warning',
            'message': 'Test alert'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_statistics(self):
        """Test alert statistics."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/alerts/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_alerts', response.data)
