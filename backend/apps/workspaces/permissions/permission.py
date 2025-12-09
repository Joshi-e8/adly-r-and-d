from rest_framework import permissions
from apps.workspaces.models import WorkspaceMember


class WorkspacePermission(permissions.BasePermission):
    """
    Custom permission to check workspace access based on user role.
    Following al-balad pattern for permissions.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        workspace_id = view.kwargs.get('workspace_id') or view.kwargs.get('pk')
        if not workspace_id:
            return True  # Let the view handle missing workspace_id
        
        try:
            member = WorkspaceMember.objects.get(
                workspace_id=workspace_id,
                user=request.user
            )
            
            # Check permissions based on HTTP method and role
            if request.method in permissions.SAFE_METHODS:
                # All members can read
                return True
            elif request.method in ['POST', 'PUT', 'PATCH']:
                # Only owners and members can create/update
                return member.role in ['owner', 'member']
            elif request.method == 'DELETE':
                # Only owners can delete
                return member.role == 'owner'
            
            return False
            
        except WorkspaceMember.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        # For workspace objects, check if user is a member
        if hasattr(obj, 'members'):
            return obj.members.filter(user=request.user).exists()
        
        # For other objects that belong to a workspace
        if hasattr(obj, 'workspace'):
            return obj.workspace.members.filter(user=request.user).exists()
        
        return False