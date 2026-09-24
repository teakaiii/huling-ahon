"""
URL configuration for Authentication module.
"""
from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserListView,
    UserDetailView,
    BarangayStaffListView,
    BarangayStaffDetailView,
    CreateBarangayStaffView,
    profile_view,
    change_password_view,
    logout_view
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    
    # User management (Admin only)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<uuid:user_id>/', UserDetailView.as_view(), name='user_detail'),
    
    # Barangay Staff management (Admin only)
    path('staff/', BarangayStaffListView.as_view(), name='staff_list'),
    path('staff/create/', CreateBarangayStaffView.as_view(), name='staff_create'),
    path('staff/<uuid:staff_id>/', BarangayStaffDetailView.as_view(), name='staff_detail'),
]
