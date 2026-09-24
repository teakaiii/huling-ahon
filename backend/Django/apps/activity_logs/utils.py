"""
Utility functions for activity logging.
"""
import json

from django.core.serializers.json import DjangoJSONEncoder

from .models import ActivityLog
from apps.authentication.models import User


def _json_safe(details):
    """
    Coerce `details` into something the JSONField can store.

    Callers routinely pass a serializer's validated_data, which holds Decimal,
    datetime and UUID values that the plain json encoder rejects. Logging is
    incidental to the request, so a value that still will not encode is kept as
    its repr rather than raising and failing the whole operation.
    """
    if details is None:
        return None

    try:
        return json.loads(json.dumps(details, cls=DjangoJSONEncoder))
    except (TypeError, ValueError):
        return {'unserializable': repr(details)}


def log_activity(user, action, entity, entity_id=None, details=None, ip_address=None, user_agent=None):
    """
    Log an activity to the database.
    
    Args:
        user: User object or None
        action: Action performed (create, update, delete, etc.)
        entity: Entity type (user, resident, etc.)
        entity_id: ID of the entity (optional)
        details: Additional details as JSON (optional)
        ip_address: IP address of the request (optional)
        user_agent: User agent string (optional)
    
    Returns:
        ActivityLog object
    """
    return ActivityLog.objects.create(
        user=user,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id else None,
        details=_json_safe(details),
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
