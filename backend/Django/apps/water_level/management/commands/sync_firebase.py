"""
Django management command to sync data from Firebase to PostgreSQL.
Run: python manage.py sync_firebase
"""

from django.core.management.base import BaseCommand
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync water level data from Firebase to PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Keep syncing the sensor reading continuously.',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Seconds between Firebase checks when --watch is enabled.',
        )

    def handle(self, *args, **options):
        interval = max(options['interval'], 1)

        if options['watch']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Watching Firebase sensor data every {interval} seconds. Press Ctrl+C to stop.'
                )
            )
            try:
                while True:
                    self.sync_once()
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Firebase watch stopped.'))
            return

        self.sync_once()

    def sync_once(self):
        self.stdout.write('Starting Firebase sync...')
        try:
            # Import Firebase service
            from backend.api.firebase_service import firebase_service
            
            # Test Firebase connection
            self.stdout.write('Testing Firebase connection...')
            if not firebase_service.test_connection():
                self.stdout.write(self.style.ERROR('Firebase connection test failed'))
                return
            
            self.stdout.write(self.style.SUCCESS('Firebase connection successful'))
            
            # Get current water level
            self.stdout.write('Fetching current water level from Firebase...')
            water_level_data = firebase_service.get_current_water_level()
            
            if water_level_data:
                self.stdout.write(f'Water level data: {water_level_data}')
                
                # Sync to PostgreSQL
                reading = firebase_service.sync_water_level_to_postgres(water_level_data)
                
                if reading:
                    self.stdout.write(self.style.SUCCESS(f'Synced water level: {reading.reading_id}'))
                else:
                    self.stdout.write(self.style.WARNING('Failed to sync water level'))
            else:
                self.stdout.write(self.style.WARNING('No water level data found in Firebase'))
            
            # Get alerts
            self.stdout.write('Fetching alerts from Firebase...')
            alerts_data = firebase_service.get_alerts()
            
            if alerts_data:
                self.stdout.write(f'Found {len(alerts_data)} alerts')
                
                # Sync to PostgreSQL
                synced_count = firebase_service.sync_alerts_to_postgres(alerts_data)
                
                self.stdout.write(self.style.SUCCESS(f'Synced {synced_count} alerts'))
            else:
                self.stdout.write(self.style.WARNING('No alerts found in Firebase'))
            
            self.stdout.write(self.style.SUCCESS('Firebase sync completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Firebase sync failed: {e}'))
            logger.error(f'Firebase sync failed: {e}', exc_info=True)
