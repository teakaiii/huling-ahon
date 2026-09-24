"""
Admin registration for Alerts module.
"""
from django.contrib import admin

from .models import FloodAlert


@admin.register(FloodAlert)
class FloodAlertAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'alert_level', 'is_active', 'reading')
    list_filter = ('alert_level', 'is_active')
    search_fields = ('message',)
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('alert_id', 'created_at')
