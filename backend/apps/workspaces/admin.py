from django.contrib import admin
from apps.workspaces.models import Workspace, WorkspaceMember, AuditLog


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug', 'owner__email']
    readonly_fields = ['slug', 'created_at', 'updated_at']


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ['workspace', 'user', 'role', 'invited_by', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['workspace__name', 'user__email']
    readonly_fields = ['joined_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['workspace', 'user', 'action', 'resource_type', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['workspace__name', 'user__email', 'action']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False