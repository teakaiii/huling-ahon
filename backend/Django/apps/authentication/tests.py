"""
Unit tests for Authentication module.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, BarangayStaff

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='staff'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'staff')
        self.assertTrue(self.user.is_active)
    
    def test_user_str(self):
        """Test user string representation."""
        self.assertEqual(str(self.user), 'testuser (Barangay Staff)')
    
    def test_is_admin_property(self):
        """Test is_admin property."""
        self.assertFalse(self.user.is_admin)
        self.user.role = 'admin'
        self.user.save()
        self.assertTrue(self.user.is_admin)
    
    def test_is_staff_user_property(self):
        """Test is_staff_user property."""
        self.assertTrue(self.user.is_staff_user)
        self.user.role = 'admin'
        self.user.save()
        self.assertFalse(self.user.is_staff_user)


class BarangayStaffModelTest(TestCase):
    """Test cases for BarangayStaff model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            role='staff'
        )
        self.staff = BarangayStaff.objects.create(
            user=self.user,
            full_name='John Doe',
            mobile_number='+639123456789',
            address='123 Test St',
            purok_zone='Zone 1'
        )
    
    def test_staff_creation(self):
        """Test staff creation."""
        self.assertEqual(self.staff.full_name, 'John Doe')
        self.assertEqual(self.staff.mobile_number, '+639123456789')
        self.assertEqual(self.staff.purok_zone, 'Zone 1')
        self.assertEqual(self.staff.status, 'active')
    
    def test_staff_str(self):
        """Test staff string representation."""
        self.assertEqual(str(self.staff), 'John Doe - Zone 1')


class AuthenticationAPITest(TestCase):
    """Test cases for Authentication API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            role='staff'
        )
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post('/api/auth/login/', {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_failure(self):
        """Test login with wrong credentials."""
        response = self.client.post('/api/auth/login/', {
            'username': 'admin',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_unauthorized(self):
        """Test profile endpoint without authentication."""
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_authorized(self):
        """Test profile endpoint with authentication."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'admin')
    
    def test_register_admin_only(self):
        """Test user registration requires admin."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': 'staff'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_register_admin_success(self):
        """Test user registration by admin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'role': 'staff'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_password_mismatch(self):
        """Test registration with password mismatch."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'differentpass',
            'role': 'staff'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
