"""
Unit tests for Notifications module.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import Notification
from apps.authentication.models import User


class NotificationModelTest(TestCase):
    """Test cases for Notification model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='staff'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            type='info',
            is_read=False
        )
    
    def test_notification_creation(self):
        """Test notification creation."""
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.message, 'This is a test notification')
        self.assertEqual(self.notification.type, 'info')
        self.assertFalse(self.notification.is_read)
    
    def test_notification_str(self):
        """Test notification string representation."""
        str_repr = str(self.notification)
        self.assertIn('Test Notification', str_repr)
    
    def test_notification_mark_as_read(self):
        """Test marking notification as read."""
        self.notification.is_read = True
        self.notification.save()
        self.assertTrue(self.notification.is_read)
    
    def test_notification_type_options(self):
        """Test notification type options."""
        valid_types = ['info', 'success', 'warning', 'danger']
        for notif_type in valid_types:
            notification = Notification.objects.create(
                user=self.user,
                title='Test',
                message='Test message',
                type=notif_type
            )
            self.assertEqual(notification.type, notif_type)


class NotificationsAPITest(TestCase):
    """Test cases for Notifications API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='staff'
        )
        
        # Create test notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                title=f'Notification {i}',
                message=f'Test message {i}',
                type=['info', 'success', 'warning', 'danger', 'info'][i],
                is_read=i < 2  # First 2 are read
            )
    
    def test_list_notifications_unauthorized(self):
        """Test list notifications without authentication."""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_notifications_authorized(self):
        """Test list notifications with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
    
    def test_user_specific_notifications(self):
        """Test notifications are user-specific."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            role='staff'
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_mark_notification_as_read(self):
        """Test mark notification as read."""
        self.client.force_authenticate(user=self.user)
        notification = Notification.objects.filter(is_read=False).first()
        response = self.client.patch(f'/api/notifications/{notification.notif_id}/', {
            'is_read': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_mark_all_as_read(self):
        """Test mark all notifications as read."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unread_count(self):
        """Test unread count endpoint."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)
