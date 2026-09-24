"""
Serializers for Authentication module.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, BarangayStaff


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user data.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add additional user data to response
        data['user'] = {
            'user_id': str(self.user.user_id),
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'full_name': getattr(self.user, 'full_name', ''),
        }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'password', 'password_confirm',
            'role', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating User model.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active']
        read_only_fields = ['user_id']


class BarangayStaffSerializer(serializers.ModelSerializer):
    """
    Serializer for BarangayStaff model.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = BarangayStaff
        fields = [
            'staff_id', 'user', 'user_id', 'full_name', 'mobile_number',
            'address', 'purok_zone', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['staff_id', 'created_at', 'updated_at']
    
    def validate_mobile_number(self, value):
        """
        Validate mobile number format.
        """
        if not value.startswith('+63'):
            raise serializers.ValidationError("Mobile number must start with +63")
        return value


class BarangayStaffCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating BarangayStaff with User.
    """
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = BarangayStaff
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'full_name', 'mobile_number', 'address', 'purok_zone', 'status'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='staff'
        )
        
        # Create staff profile
        staff = BarangayStaff.objects.create(user=user, **validated_data)
        return staff


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
