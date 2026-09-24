"""
Admin registration for Water Level module.
"""
from django.contrib import admin

from .models import WaterLevelReading


@admin.register(WaterLevelReading)
class WaterLevelReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'water_level_cm', 'status', 'sensor_status', 'gsm_status', 'firebase_synced')
    list_filter = ('status', 'sensor_status', 'gsm_status', 'firebase_synced')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('reading_id', 'created_at')
