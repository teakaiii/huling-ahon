"""
Test configuration and utilities for the Django backend.
"""

import os
import sys
from django.conf import settings
from django.test.utils import get_runner

# Configure Django settings
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flood_detection.settings')
    
    # Initialize Django
    import django
    django.setup()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run tests
    failures = test_runner.run_tests(['apps'])
    
    # Exit with appropriate code
    sys.exit(bool(failures))
