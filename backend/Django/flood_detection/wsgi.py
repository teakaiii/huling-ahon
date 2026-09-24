"""
WSGI config for flood_detection project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flood_detection.settings')

application = get_wsgi_application()
