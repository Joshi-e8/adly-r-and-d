from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.authentication.models import User, OTPToken, User2FA


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_verified', 'two_factor_auth', 'is_active', 'created_at']
    list_filter = ['is_verified', 'two_factor_auth', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'two_factor_auth', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'purpose', 'expires_at', 'used_at', 'created_at']
    list_filter = ['purpose', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['created_at']


@admin.register(User2FA)
class User2FAAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_enabled', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['secret', 'created_at']