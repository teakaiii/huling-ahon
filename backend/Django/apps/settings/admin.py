"""
Admin registration for System Settings module.
"""
from django.contrib import admin

from .models import SystemSetting


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at', 'updated_by')
    search_fields = ('key', 'value', 'description')
    ordering = ('key',)
    readonly_fields = ('setting_id', 'updated_at')
