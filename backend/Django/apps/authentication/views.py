"""
Views for Authentication module.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash
from .models import User, BarangayStaff
from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    BarangayStaffSerializer,
    BarangayStaffCreateSerializer,
    ChangePasswordSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view with additional user data.
    """
    pass


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Only admins can create new users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='user',
            details={'username': serializer.validated_data['username']}
        )
        serializer.save()


class UserListView(generics.ListAPIView):
    """
    API endpoint to list all users.
    Only admins can access this endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a user.
    Only admins can access this endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    lookup_field = 'user_id'
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='user',
            entity_id=str(self.get_object().user_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='user',
            entity_id=str(instance.user_id),
            details={'username': instance.username}
        )
        instance.delete()


class BarangayStaffListView(generics.ListAPIView):
    """
    API endpoint to list all barangay staff.
    Only admins can access this endpoint.
    """
    queryset = BarangayStaff.objects.select_related('user').all()
    serializer_class = BarangayStaffSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filterset_fields = ['status', 'purok_zone']
    search_fields = ['full_name', 'mobile_number', 'purok_zone']
    ordering_fields = ['created_at', 'full_name']
    ordering = ['-created_at']


class BarangayStaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a barangay staff.
    Only admins can access this endpoint.
    """
    queryset = BarangayStaff.objects.select_related('user').all()
    serializer_class = BarangayStaffSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    lookup_field = 'staff_id'
    
    def perform_update(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='update',
            entity='barangay_staff',
            entity_id=str(self.get_object().staff_id),
            details=serializer.validated_data
        )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='delete',
            entity='barangay_staff',
            entity_id=str(instance.staff_id),
            details={'full_name': instance.full_name}
        )
        instance.delete()


class CreateBarangayStaffView(generics.CreateAPIView):
    """
    API endpoint to create a new barangay staff with user account.
    Only admins can access this endpoint.
    """
    queryset = BarangayStaff.objects.all()
    serializer_class = BarangayStaffCreateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=self.request.user,
            action='create',
            entity='barangay_staff',
            details={'full_name': serializer.validated_data['full_name']}
        )
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """
    API endpoint to get current user profile.
    """
    user = request.user
    
    # Get staff profile if exists
    staff_profile = None
    if hasattr(user, 'staff_profile'):
        staff_profile = BarangayStaffSerializer(user.staff_profile).data
    
    data = {
        'user': UserSerializer(user).data,
        'staff_profile': staff_profile
    }
    
    return Response(data)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """
    API endpoint to change user password.
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=user,
            action='change_password',
            entity='user',
            entity_id=str(user.user_id)
        )
        
        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout.
    """
    try:
        # Blacklist the refresh token
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log activity
        from apps.activity_logs.utils import log_activity
        log_activity(
            user=request.user,
            action='logout',
            entity='user',
            entity_id=str(request.user.user_id)
        )
        
        return Response(
            {'message': 'Successfully logged out.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
