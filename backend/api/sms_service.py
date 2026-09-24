"""
SMS Notification Service for Django Backend
This module handles:
- Sending SMS alerts to residents during flood conditions
- Managing SMS delivery status
- Rate limiting and cooldown periods
- Integration with Django models for logging
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from django.conf import settings
from django.utils import timezone
from apps.residents.models import Resident
from apps.alerts.models import FloodAlert
from apps.sms.models import SMSLog
from apps.water_level.models import WaterLevelReading

logger = logging.getLogger(__name__)


class SMSService:
    """
    SMS Notification Service for sending flood alerts to residents.
    """
    
    def __init__(self):
        self.sms_enabled = settings.SMS_ENABLED
        self.max_sms_per_hour = settings.MAX_SMS_PER_HOUR
        self.warning_threshold = settings.WARNING_THRESHOLD
        self.danger_threshold = settings.DANGER_THRESHOLD
    
    def check_flood_conditions(self) -> Dict:
        """
        Check current water level and determine if SMS alerts should be sent.
        
        Returns:
            Dict with flood status and alert level
        """
        try:
            # Get latest water level reading
            latest_reading = WaterLevelReading.objects.order_by('-timestamp').first()
            
            if not latest_reading:
                return {
                    'should_alert': False,
                    'reason': 'No water level reading available'
                }
            
            water_level = latest_reading.water_level_cm
            status = latest_reading.status
            
            # Determine if alert should be sent
            should_alert = False
            alert_level = None
            
            if status == 'Danger' and water_level >= self.danger_threshold:
                should_alert = True
                alert_level = 'Danger'
            elif status == 'Warning' and water_level >= self.warning_threshold:
                should_alert = True
                alert_level = 'Warning'
            
            return {
                'should_alert': should_alert,
                'alert_level': alert_level,
                'water_level': water_level,
                'status': status,
                'timestamp': latest_reading.timestamp
            }
            
        except Exception as e:
            logger.error(f"Error checking flood conditions: {e}")
            return {
                'should_alert': False,
                'reason': f'Error: {str(e)}'
            }
    
    def get_active_residents(self) -> List[Resident]:
        """
        Get list of active residents with SMS enabled.
        
        Returns:
            List of Resident objects
        """
        try:
            residents = Resident.objects.filter(
                status='active',
                sms_enabled=True
            ).order_by('purok_zone', 'full_name')
            
            logger.info(f"Found {residents.count()} active residents with SMS enabled")
            return residents
            
        except Exception as e:
            logger.error(f"Error getting active residents: {e}")
            return []
    
    def check_rate_limit(self) -> bool:
        """
        Check if SMS rate limit has been exceeded.
        
        Returns:
            True if rate limit OK, False if exceeded
        """
        try:
            # Count SMS sent in the last hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            sms_count = SMSLog.objects.filter(
                sent_at__gte=one_hour_ago
            ).count()
            
            if sms_count >= self.max_sms_per_hour:
                logger.warning(f"SMS rate limit exceeded: {sms_count}/{self.max_sms_per_hour}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
    
    def check_cooldown(self, resident_id: str, alert_level: str) -> bool:
        """
        Check if resident is in cooldown period for this alert level.
        
        Args:
            resident_id: ID of the resident
            alert_level: Alert level to check
            
        Returns:
            True if cooldown OK, False if in cooldown
        """
        try:
            # Check if SMS was sent to this resident for this alert level in the last 5 minutes
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            
            recent_sms = SMSLog.objects.filter(
                resident_id=resident_id,
                alert__alert_level=alert_level,
                sent_at__gte=five_minutes_ago
            ).exists()
            
            if recent_sms:
                logger.info(f"Resident {resident_id} in cooldown for {alert_level} alert")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return False
    
    def create_alert_message(self, alert_level: str, water_level: float) -> str:
        """
        Create SMS alert message.
        
        Args:
            alert_level: Alert level (Warning or Danger)
            water_level: Current water level in cm
            
        Returns:
            Formatted SMS message
        """
        message = f"BARANGAY TONSUYA FLOOD {alert_level.upper()}\n\n"
        message += f"Current Flood Level: {alert_level}\n"
        message += f"Water Level: {water_level} cm\n\n"
        
        if alert_level == 'Danger':
            message += "Water levels have reached a critical level.\n"
            message += "Residents are advised to prepare for immediate evacuation.\n"
        elif alert_level == 'Warning':
            message += "Water levels are rising.\n"
            message += "Residents are advised to monitor the situation closely.\n"
        
        message += f"\nDate: {datetime.now().strftime('%Y-%m-%d')}\n"
        message += f"Time: {datetime.now().strftime('%H:%M')}\n"
        message += "\nPlease stay safe."
        
        return message
    
    def send_sms(self, recipient: str, message: str, alert_id: str = None,
                 resident: Resident = None) -> SMSLog:
        """
        Send SMS message (placeholder for actual SMS gateway integration).

        Args:
            recipient: Mobile number of recipient
            message: SMS message content
            alert_id: Optional alert ID for logging
            resident: Resident the message is addressed to. Required, because
                SMSLog.resident is not nullable; resolved from the number when
                the caller does not supply it.

        Returns:
            SMSLog object
        """
        if resident is None:
            resident = Resident.objects.filter(mobile_number=recipient).first()
        if resident is None:
            raise ValueError(
                f"No resident registered with mobile number {recipient}; "
                "SMSLog requires one."
            )

        try:
            # In a real implementation, this would integrate with an SMS gateway
            # For now, we'll simulate SMS sending
            
            logger.info(f"Sending SMS to {recipient}")
            logger.info(f"Message: {message[:100]}...")
            
            # Simulate successful delivery
            delivery_status = 'delivered'
            error_message = None
            
            # Create SMS log
            sms_log = SMSLog.objects.create(
                alert_id=alert_id,
                resident=resident,
                recipient=recipient,
                message=message,
                delivery_status=delivery_status,
                error_message=error_message
            )
            
            logger.info(f"SMS sent successfully to {recipient}")
            return sms_log
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            
            # Create failed SMS log
            sms_log = SMSLog.objects.create(
                alert_id=alert_id,
                resident=resident,
                recipient=recipient,
                message=message,
                delivery_status='failed',
                error_message=str(e)
            )
            
            return sms_log
    
    def send_flood_alert(self, alert_level: str, water_level: float) -> Dict:
        """
        Send flood alert to all active residents.
        
        Args:
            alert_level: Alert level (Warning or Danger)
            water_level: Current water level in cm
            
        Returns:
            Dict with sending statistics
        """
        if not self.sms_enabled:
            return {
                'success': False,
                'reason': 'SMS notifications are disabled'
            }
        
        # Check rate limit
        if not self.check_rate_limit():
            return {
                'success': False,
                'reason': 'SMS rate limit exceeded'
            }
        
        # Get active residents
        residents = self.get_active_residents()
        
        if not residents:
            return {
                'success': False,
                'reason': 'No active residents with SMS enabled'
            }
        
        # Create alert message
        message = self.create_alert_message(alert_level, water_level)
        
        # Create flood alert record
        try:
            latest_reading = WaterLevelReading.objects.order_by('-timestamp').first()
            alert = FloodAlert.objects.create(
                reading=latest_reading,
                alert_level=alert_level,
                message=message,
                timestamp=timezone.now()
            )
        except Exception as e:
            logger.error(f"Error creating flood alert: {e}")
            return {
                'success': False,
                'reason': f'Error creating alert: {str(e)}'
            }
        
        # Send SMS to residents
        sent_count = 0
        failed_count = 0
        skipped_count = 0
        
        for resident in residents:
            # Check cooldown
            if not self.check_cooldown(str(resident.resident_id), alert_level):
                skipped_count += 1
                continue
            
            # Send SMS
            try:
                sms_log = self.send_sms(
                    recipient=resident.mobile_number,
                    message=message,
                    alert_id=str(alert.alert_id),
                    resident=resident
                )

                if sms_log.delivery_status == 'delivered':
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending SMS to {resident.mobile_number}: {e}")
                failed_count += 1
        
        statistics = {
            'success': True,
            'alert_level': alert_level,
            'water_level': water_level,
            'total_residents': residents.count(),
            'sent': sent_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'alert_id': str(alert.alert_id)
        }
        
        logger.info(f"Flood alert sent: {statistics}")
        return statistics
    
    def send_test_sms(self, recipient: str) -> Dict:
        """
        Send a test SMS message.
        
        Args:
            recipient: Mobile number to send test to
            
        Returns:
            Dict with result
        """
        message = "TEST MESSAGE - Barangay Tonsuya Flood Detection System\n\nThis is a test SMS to verify the notification system is working correctly."
        
        try:
            sms_log = self.send_sms(recipient=recipient, message=message)
            
            return {
                'success': sms_log.delivery_status == 'delivered',
                'delivery_status': sms_log.delivery_status,
                'sms_id': str(sms_log.sms_id)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
sms_service = SMSService()
