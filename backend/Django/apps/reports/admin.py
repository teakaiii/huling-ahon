"""
Admin registration for Reports module.
"""
from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'report_type', 'file_format', 'record_count', 'generated_by')
    list_filter = ('report_type', 'file_format')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('report_id', 'created_at')
