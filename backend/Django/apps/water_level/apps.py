"""
App configuration for the Water Level module.
"""
from django.apps import AppConfig


class WaterLevelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.water_level'
    verbose_name = 'Water Level'

    def ready(self):
        # Registers the flood-alert signal handler.
        from . import signals  # noqa: F401
