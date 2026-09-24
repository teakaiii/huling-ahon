"""
URL configuration for Settings module.
"""
from django.urls import path
from .views import (
    SystemSettingListView,
    SystemSettingDetailView,
    SystemSettingCreateView,
    get_setting_view,
    update_setting_view,
    flood_thresholds_view
)

urlpatterns = [
    path('', SystemSettingListView.as_view(), name='setting_list'),
    path('<uuid:setting_id>/', SystemSettingDetailView.as_view(), name='setting_detail'),
    path('create/', SystemSettingCreateView.as_view(), name='setting_create'),
    path('key/<str:key>/', get_setting_view, name='get_setting'),
    path('key/<str:key>/update/', update_setting_view, name='update_setting'),
    path('flood-thresholds/', flood_thresholds_view, name='flood_thresholds'),
]
