"""
Admin registration for Activity Logs module.
"""
from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity', 'ip_address')
    list_filter = ('action', 'entity')
    search_fields = ('entity_id', 'ip_address', 'user_agent')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('log_id', 'timestamp')
