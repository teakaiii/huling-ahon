"""
Admin registration for Notifications module.
"""
from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'title', 'type', 'user', 'is_read')
    list_filter = ('type', 'is_read')
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('notif_id', 'created_at')
