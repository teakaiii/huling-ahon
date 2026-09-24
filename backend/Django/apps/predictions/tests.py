"""
Unit tests for Predictions module.
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import Prediction, AIModel
from apps.authentication.models import User


class PredictionModelTest(TestCase):
    """Test cases for Prediction model."""
    
    def setUp(self):
        self.prediction = Prediction.objects.create(
            water_level_cm=65,
            flood_probability=75.5,
            severity='high',
            alert_level='Warning',
            confidence_score=85.0,
            timestamp=timezone.now()
        )
    
    def test_prediction_creation(self):
        """Test prediction creation."""
        self.assertEqual(self.prediction.water_level_cm, 65)
        self.assertEqual(self.prediction.flood_probability, 75.5)
        self.assertEqual(self.prediction.severity, 'high')
        self.assertEqual(self.prediction.alert_level, 'Warning')
    
    def test_prediction_str(self):
        """Test prediction string representation."""
        str_repr = str(self.prediction)
        self.assertIn('Warning', str_repr)
    
    def test_severity_options(self):
        """Test severity options."""
        valid_severities = ['low', 'medium', 'high', 'critical']
        for severity in valid_severities:
            prediction = Prediction.objects.create(
                water_level_cm=50,
                flood_probability=50.0,
                severity=severity,
                alert_level='Alert',
                confidence_score=70.0
            )
            self.assertEqual(prediction.severity, severity)


class AIModelModelTest(TestCase):
    """Test cases for AIModel model."""
    
    def setUp(self):
        self.ai_model = AIModel.objects.create(
            model_name='RandomForest',
            version='1.0',
            accuracy=0.92,
            precision=0.90,
            recall=0.88,
            f1_score=0.89,
            is_active=True
        )
    
    def test_ai_model_creation(self):
        """Test AI model creation."""
        self.assertEqual(self.ai_model.model_name, 'RandomForest')
        self.assertEqual(self.ai_model.version, '1.0')
        self.assertEqual(self.ai_model.accuracy, 0.92)
        self.assertTrue(self.ai_model.is_active)
    
    def test_ai_model_str(self):
        """Test AI model string representation."""
        str_repr = str(self.ai_model)
        self.assertIn('RandomForest', str_repr)
        self.assertIn('1.0', str_repr)


class PredictionsAPITest(TestCase):
    """Test cases for Predictions API endpoints."""
    
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
        
        # Create test predictions
        for i in range(3):
            Prediction.objects.create(
                water_level_cm=40 + i * 15,
                flood_probability=50 + i * 15,
                severity=['low', 'medium', 'high'][i],
                alert_level=['Normal', 'Alert', 'Warning'][i],
                confidence_score=80 + i,
                timestamp=timezone.now() - timezone.timedelta(hours=i)
            )
    
    def test_list_predictions_unauthorized(self):
        """Test list predictions without authentication."""
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_predictions_authorized(self):
        """Test list predictions with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_latest_prediction(self):
        """Test get latest prediction."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/predictions/latest/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('water_level_cm', response.data)
    
    def test_create_prediction_admin_only(self):
        """Test create prediction requires admin."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/predictions/create/', {
            'water_level_cm': 50,
            'flood_probability': 60.0,
            'severity': 'medium',
            'alert_level': 'Alert',
            'confidence_score': 75.0
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_prediction_admin_success(self):
        """Test create prediction by admin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/predictions/create/', {
            'water_level_cm': 50,
            'flood_probability': 60.0,
            'severity': 'medium',
            'alert_level': 'Alert',
            'confidence_score': 75.0
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_statistics(self):
        """Test prediction statistics."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/predictions/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_predictions', response.data)
