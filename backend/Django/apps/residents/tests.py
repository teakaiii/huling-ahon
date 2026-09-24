"""
Unit tests for Residents module.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Resident
from apps.authentication.models import User


class ResidentModelTest(TestCase):
    """Test cases for Resident model."""
    
    def setUp(self):
        self.resident = Resident.objects.create(
            full_name='John Doe',
            mobile_number='+639123456789',
            address='123 Test St',
            purok_zone='Zone 1',
            status='active',
            sms_enabled=True
        )
    
    def test_resident_creation(self):
        """Test resident creation."""
        self.assertEqual(self.resident.full_name, 'John Doe')
        self.assertEqual(self.resident.mobile_number, '+639123456789')
        self.assertEqual(self.resident.purok_zone, 'Zone 1')
        self.assertEqual(self.resident.status, 'active')
        self.assertTrue(self.resident.sms_enabled)
    
    def test_resident_str(self):
        """Test resident string representation."""
        self.assertEqual(str(self.resident), 'John Doe - Zone 1')
    
    def test_mobile_number_validation_valid(self):
        """Test valid mobile number."""
        resident = Resident(
            full_name='Jane Doe',
            mobile_number='+639876543210',
            address='456 Test St',
            purok_zone='Zone 2'
        )
        resident.full_clean()  # Should not raise
        resident.save()
        self.assertEqual(Resident.objects.count(), 2)
    
    def test_mobile_number_validation_invalid(self):
        """Test invalid mobile number."""
        resident = Resident(
            full_name='Invalid User',
            mobile_number='12345',
            address='789 Test St',
            purok_zone='Zone 3'
        )
        with self.assertRaises(Exception):
            resident.full_clean()


class ResidentsAPITest(TestCase):
    """Test cases for Residents API endpoints."""
    
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
        
        # Create test residents
        for i in range(3):
            Resident.objects.create(
                full_name=f'Resident {i}',
                mobile_number=f'+63912345678{i}',
                address=f'{i} Test St',
                purok_zone=f'Zone {i+1}',
                status='active',
                sms_enabled=True
            )
    
    def test_list_residents_unauthorized(self):
        """Test list residents without authentication."""
        response = self.client.get('/api/residents/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_residents_authorized(self):
        """Test list residents with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/residents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_resident_admin_only(self):
        """Test create resident requires admin."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/residents/create/', {
            'full_name': 'New Resident',
            'mobile_number': '+6391234567890',
            'address': 'New Address',

            'purok_zone': 'Zone 4',
            'status': 'active',
            'sms_enabled': True
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_resident_admin_success(self):
        """Test create resident by admin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/residents/create/', {
            'full_name': 'New Resident',
            'mobile_number': '+6391234567890',
            'address': 'New Address',
            'purok_zone': 'Zone 4',
            'status': 'active',
            'sms_enabled': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_resident(self):
        """Test update resident."""
        self.client.force_authenticate(user=self.admin_user)
        resident = Resident.objects.first()
        response = self.client.put(f'/api/residents/{resident.resident_id}/', {
            'full_name': 'Updated Name',
            'mobile_number': resident.mobile_number,
            'address': resident.address,
            'purok_zone': resident.purok_zone,
            'status': 'inactive',
            'sms_enabled': False
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_resident(self):
        """Test delete resident."""
        self.client.force_authenticate(user=self.admin_user)
        resident = Resident.objects.first()
        response = self.client.delete(f'/api/residents/{resident.resident_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_statistics(self):
        """Test resident statistics."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/residents/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_residents', response.data)
        self.assertIn('active_residents', response.data)
