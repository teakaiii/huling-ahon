"""
URL configuration for Water Level module.
"""
from django.urls import path
from .views import (
    WaterLevelReadingListView,
    WaterLevelReadingDetailView,
    WaterLevelReadingCreateView,
    public_water_level_ingest_view,
    current_water_level_view,
    water_level_history_view,
    water_level_statistics_view
)

urlpatterns = [
    path('readings/', WaterLevelReadingListView.as_view(), name='reading_list'),
    path('readings/<uuid:reading_id>/', WaterLevelReadingDetailView.as_view(), name='reading_detail'),
    path('create/', WaterLevelReadingCreateView.as_view(), name='reading_create_short'),
    path('readings/create/', WaterLevelReadingCreateView.as_view(), name='reading_create'),
    path('public-ingest/', public_water_level_ingest_view, name='public_ingest'),
    path('current/', current_water_level_view, name='current_level'),
    path('history/', water_level_history_view, name='level_history'),
    path('statistics/', water_level_statistics_view, name='level_statistics'),
]
