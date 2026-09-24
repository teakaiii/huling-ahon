"""
URL configuration for Residents module.
"""
from django.urls import path
from .views import (
    ResidentListCreateView,
    ResidentDetailView,
    ResidentCreateView,
    ResidentImportView,
    active_residents_view,
    residents_by_purok_view,
    resident_statistics_view
)

urlpatterns = [
    path('', ResidentListCreateView.as_view(), name='resident_list_create'),
    path('import/', ResidentImportView.as_view(), name='resident_import'),
    path('<uuid:resident_id>/', ResidentDetailView.as_view(), name='resident_detail'),
    path('active/', active_residents_view, name='active_residents'),
    path('purok/<str:purok_zone>/', residents_by_purok_view, name='residents_by_purok'),
    path('statistics/', resident_statistics_view, name='resident_statistics'),
]
