"""
URL configuration for flood_detection project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import admin as _admin_branding  # noqa: F401  (applies admin site branding)

schema_view = get_schema_view(
    openapi.Info(
        title="AHON FloodWatch API",
        default_version='v1',
        description="API documentation for AHON FloodWatch - Barangay Tonsuya Flood Detection System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@barangay-tonsuya.gov.ph"),
        license=openapi.License(name="BSD License"),
        x_logo={
            "url": "/static/images/logo.png",
            "altText": "AHON FloodWatch Logo",
            "backgroundColor": "#FFFFFF",
        }
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

@api_view(['GET'])
def api_root(request):
    """
    API root endpoint that lists all available API endpoints.
    """
    return Response({
        'message': 'Welcome to AHON FloodWatch API',
        'version': 'v1',
        'endpoints': {
            'authentication': '/api/auth/',
            'water_level': '/api/water-level/',
            'residents': '/api/residents/',
            'alerts': '/api/alerts/',
            'sms': '/api/sms/',
            'predictions': '/api/predictions/',
            'reports': '/api/reports/',
            'notifications': '/api/notifications/',
            'activity_logs': '/api/activity-logs/',
            'settings': '/api/settings/',
            'dashboard': '/api/dashboard/',
            'documentation': '/swagger/',
            'admin': '/admin/',
        },
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'swagger_json': '/swagger.json',
        }
    })

urlpatterns = [
    # Root URL - Welcome page
    path('', lambda request: redirect('admin/')),
    
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API Root
    path('api/', api_root),
    
    # API Endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/water-level/', include('apps.water_level.urls')),
    path('api/residents/', include('apps.residents.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/sms/', include('apps.sms.urls')),
    path('api/predictions/', include('apps.predictions.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/activity-logs/', include('apps.activity_logs.urls')),
    path('api/settings/', include('apps.settings.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
]
