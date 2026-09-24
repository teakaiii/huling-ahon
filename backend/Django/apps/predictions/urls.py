"""
URL configuration for AI Predictions module.
"""
from django.urls import path
from .views import (
    PredictionListView,
    PredictionDetailView,
    PredictionCreateView,
    latest_prediction_view,
    prediction_statistics_view,
    AIModelListView,
    AIModelDetailView,
    AIModelCreateView,
    active_model_view
)

urlpatterns = [
    # Prediction endpoints
    path('', PredictionListView.as_view(), name='prediction_list'),
    path('<uuid:prediction_id>/', PredictionDetailView.as_view(), name='prediction_detail'),
    path('create/', PredictionCreateView.as_view(), name='prediction_create'),
    path('latest/', latest_prediction_view, name='latest_prediction'),
    path('statistics/', prediction_statistics_view, name='prediction_statistics'),
    
    # AI Model endpoints
    path('models/', AIModelListView.as_view(), name='ai_model_list'),
    path('models/<uuid:model_id>/', AIModelDetailView.as_view(), name='ai_model_detail'),
    path('models/create/', AIModelCreateView.as_view(), name='ai_model_create'),
    path('models/active/', active_model_view, name='active_model'),
]
