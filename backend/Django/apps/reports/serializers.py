"""
Serializers for Reports module.
"""
from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model.
    """
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'report_id', 'report_type', 'generated_by', 'generated_by_username',
            'start_date', 'end_date', 'file_path', 'file_format',
            'record_count', 'created_at'
        ]
        read_only_fields = ['report_id', 'created_at']


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating reports.
    """
    class Meta:
        model = Report
        fields = [
            'report_type', 'generated_by', 'start_date', 'end_date',
            'file_format'
        ]
