"""
Unit tests for Reports module.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import Report
from apps.authentication.models import User


class ReportModelTest(TestCase):
    """Test cases for Report model."""
    
    def setUp(self):
        self.report = Report.objects.create(
            report_type='daily',
            start_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now(),
            file_format='pdf',
            record_count=100,
            generated_by=User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='adminpass123',
                role='admin'
            )
        )
    
    def test_report_creation(self):
        """Test report creation."""
        self.assertEqual(self.report.report_type, 'daily')
        self.assertEqual(self.report.file_format, 'pdf')
        self.assertEqual(self.report.record_count, 100)
    
    def test_report_str(self):
        """Test report string representation."""
        str_repr = str(self.report)
        self.assertIn('daily', str_repr)
    
    def test_report_type_options(self):
        """Test report type options."""
        valid_types = ['daily', 'weekly', 'monthly', 'annual']
        for report_type in valid_types:
            report = Report.objects.create(
                report_type=report_type,
                start_date=timezone.now() - timezone.timedelta(days=1),
                end_date=timezone.now(),
                file_format='pdf',
                record_count=50,
                generated_by=self.report.generated_by
            )
            self.assertEqual(report.report_type, report_type)


class ReportsAPITest(TestCase):
    """Test cases for Reports API endpoints."""
    
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
        
        # Create test reports
        for i in range(3):
            Report.objects.create(
                report_type=['daily', 'weekly', 'monthly'][i],
                start_date=timezone.now() - timezone.timedelta(days=i+1),
                end_date=timezone.now(),
                file_format='pdf',
                record_count=100 * (i+1),
                generated_by=self.admin_user
            )
    
    def test_list_reports_unauthorized(self):
        """Test list reports without authentication."""
        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_reports_authorized(self):
        """Test list reports with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_create_report_admin_only(self):
        """Test create report requires admin."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/reports/create/', {
            'report_type': 'daily',
            'file_format': 'pdf'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_report_admin_success(self):
        """Test create report by admin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/reports/create/', {
            'report_type': 'daily',
            'file_format': 'pdf'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_generate_report(self):
        """Test generate report endpoint."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/reports/generate/?type=daily&format=pdf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_statistics(self):
        """Test report statistics."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/reports/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reports', response.data)
