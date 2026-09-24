"""
Admin registration for Authentication module.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import BarangayStaff, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('user_id', 'created_at', 'updated_at', 'last_login', 'date_joined')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Barangay Role', {'fields': ('role',)}),
        ('Audit', {'fields': ('user_id', 'created_at', 'updated_at')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Barangay Role', {'fields': ('role',)}),
    )


@admin.register(BarangayStaff)
class BarangayStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'mobile_number', 'purok_zone', 'status', 'user')
    list_filter = ('status', 'purok_zone')
    search_fields = ('full_name', 'mobile_number', 'address')
    ordering = ('full_name',)
    readonly_fields = ('staff_id', 'created_at', 'updated_at')
