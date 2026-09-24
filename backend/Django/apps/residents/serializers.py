"""
Serializers for Residents module.
"""
import re
from rest_framework import serializers
from .models import Resident


def normalize_mobile_number(value):
    value = (value or '').strip()
    digits = re.sub(r'\D', '', value)

    if digits.startswith('63'):
        digits = digits[2:]

    if len(digits) != 10 or not digits.isdigit():
        raise serializers.ValidationError(
            "Mobile number must contain exactly 10 digits after +63 (e.g. 9123456789)."
        )

    return f'+63{digits}'


class ResidentSerializer(serializers.ModelSerializer):
    """
    Serializer for Resident model.
    """
    class Meta:
        model = Resident
        fields = [
            'resident_id', 'full_name', 'mobile_number', 'address',
            'purok_zone', 'status', 'sms_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['resident_id', 'created_at', 'updated_at']


class ResidentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating residents.
    """
    class Meta:
        model = Resident
        fields = [
            'full_name', 'mobile_number', 'address', 'purok_zone', 'status', 'sms_enabled'
        ]
    
    def validate_mobile_number(self, value):
        """
        Normalize and validate mobile number format.
        """
        return normalize_mobile_number(value)


class ResidentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating residents.
    """
    class Meta:
        model = Resident
        fields = [
            'full_name', 'mobile_number', 'address', 'purok_zone', 'status', 'sms_enabled'
        ]
    
    def validate_mobile_number(self, value):
        """
        Normalize and validate mobile number format.
        """
        return normalize_mobile_number(value)
