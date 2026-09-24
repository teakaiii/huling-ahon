"""
Admin registration for SMS Logs module.
"""
from django.contrib import admin

from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'recipient', 'delivery_status', 'resident', 'alert')
    list_filter = ('delivery_status',)
    search_fields = ('recipient', 'message')
    date_hierarchy = 'sent_at'
    ordering = ('-sent_at',)
    readonly_fields = ('sms_id', 'sent_at')
