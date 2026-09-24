"""
Admin registration for Residents module.
"""
from django.contrib import admin

from .models import Resident


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'mobile_number', 'purok_zone', 'status', 'sms_enabled')
    list_filter = ('status', 'sms_enabled', 'purok_zone')
    search_fields = ('full_name', 'mobile_number', 'address')
    ordering = ('full_name',)
    readonly_fields = ('resident_id', 'created_at', 'updated_at')
