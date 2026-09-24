"""
Signal handlers for Water Level readings.

Escalating into a Warning or Danger reading sends the flood alert SMS to
residents, so alerting does not depend on someone watching the dashboard and
pressing the manual button.
"""
import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import WaterLevelReading

logger = logging.getLogger(__name__)

ALERTING_STATUSES = ('Warning', 'Danger')


@receiver(post_save, sender=WaterLevelReading, dispatch_uid='water_level_flood_alert')
def send_flood_alert_on_escalation(sender, instance, created, **kwargs):
    if not created or instance.status not in ALERTING_STATUSES:
        return

    if not settings.SMS_ENABLED:
        logger.info('SMS disabled; not alerting for %s reading', instance.status)
        return

    # Fire on the transition only. The sensor reports every few seconds, and
    # send_flood_alert() records a FloodAlert per call, so alerting on every
    # reading would bury the alert list while the water simply stays high.
    previous = (
        WaterLevelReading.objects
        .exclude(pk=instance.pk)
        .order_by('-timestamp')
        .first()
    )
    if previous is not None and previous.status == instance.status:
        return

    # Imported here so the app registry is ready and to avoid a circular import.
    from backend.api.sms_service import SMSService

    try:
        result = SMSService().send_flood_alert(
            alert_level=instance.status,
            water_level=float(instance.water_level_cm),
        )
        logger.info('Flood alert triggered by reading %s: %s', instance.reading_id, result)
    except Exception:
        # Alerting must never break sensor ingestion.
        logger.exception('Failed to send flood alert for reading %s', instance.reading_id)
