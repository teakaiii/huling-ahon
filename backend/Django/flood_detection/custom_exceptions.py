"""
Custom exception handler for REST Framework.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST Framework.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': str(exc),
            'details': response.data if hasattr(response, 'data') else None
        }
        
        response.data = custom_response_data
        
        # Log the error
        logger.error(
            f"Exception: {exc}, "
            f"Status: {response.status_code}, "
            f"View: {context['view'].__class__.__name__}"
        )
    
    return response
