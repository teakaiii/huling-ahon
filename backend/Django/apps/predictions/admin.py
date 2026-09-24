"""
Admin registration for Predictions module.
"""
from django.contrib import admin

from .models import AIModel, Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'flood_probability', 'severity', 'alert_level', 'confidence_score')
    list_filter = ('severity', 'alert_level')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('prediction_id', 'created_at')


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_type', 'version', 'accuracy', 'is_active', 'trained_at')
    list_filter = ('model_type', 'is_active')
    search_fields = ('model_name', 'version')
    ordering = ('-trained_at',)
    readonly_fields = ('model_id', 'created_at')
