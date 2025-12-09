from django.urls import path
from apps.workspaces.v1.views.workspace import WorkspaceView, WorkspaceMemberView, AuditLogView

# Workspace URLs following al-balad pattern
workspace_list_view = WorkspaceView.as_view({
    'get': 'list',
    'post': 'create'
})

workspace_detail_view = WorkspaceView.as_view({
    'get': 'retrieve',
    'patch': 'update',
    'delete': 'destroy'
})

# Member management URLs
member_list_view = WorkspaceMemberView.as_view({
    'get': 'list'
})

invite_member_view = WorkspaceMemberView.as_view({
    'post': 'invite_member'
})

update_member_role_view = WorkspaceMemberView.as_view({
    'patch': 'update_role'
})

remove_member_view = WorkspaceMemberView.as_view({
    'delete': 'remove_member'
})

# Audit log URLs
audit_log_list_view = AuditLogView.as_view({
    'get': 'list'
})

urlpatterns = [
    # Workspace endpoints
    path('', workspace_list_view, name='workspace_list_create'),
    path('<uuid:pk>/', workspace_detail_view, name='workspace_detail'),
    
    # Member management endpoints
    path('<uuid:workspace_id>/members/', member_list_view, name='workspace_members'),
    path('<uuid:workspace_id>/members/invite/', invite_member_view, name='invite_member'),
    path('<uuid:workspace_id>/members/<uuid:user_id>/role/', update_member_role_view, name='update_member_role'),
    path('<uuid:workspace_id>/members/<uuid:user_id>/remove/', remove_member_view, name='remove_member'),
    
    # Audit log endpoints
    path('<uuid:workspace_id>/audit-logs/', audit_log_list_view, name='audit_logs'),
]