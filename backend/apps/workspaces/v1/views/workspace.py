import traceback
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from apps.workspaces.models import Workspace, WorkspaceMember, AuditLog
from apps.workspaces.v1.serializer.workspace import (
    WorkspaceSerializer,
    WorkspaceMemberSerializer,
    InviteMemberSerializer,
    UpdateMemberRoleSerializer,
    AuditLogSerializer
)
from apps.workspaces.permissions.permission import WorkspacePermission


class WorkspaceView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        serializer_mapping = {
            'list': WorkspaceSerializer,
            'create': WorkspaceSerializer,
            'retrieve': WorkspaceSerializer,
            'update': WorkspaceSerializer,
            'partial_update': WorkspaceSerializer,
        }
        return serializer_mapping.get(self.action, WorkspaceSerializer)
    
    def get_queryset(self):
        return Workspace.objects.filter(
            members__user=self.request.user
        ).distinct()
    
    def list(self, request, *args, **kwargs):
        """List user workspaces"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True, context={'request': request})
            
            response.update({
                'result': 'success',
                'message': _('Workspaces fetched successfully'),
                'records': serializer.data
            })
            
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def create(self, request, *args, **kwargs):
        """Create new workspace"""
        response, status_code = {}, status.HTTP_201_CREATED
        
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                workspace = serializer.save()
                
                # Log the action
                AuditLog.objects.create(
                    workspace=workspace,
                    user=request.user,
                    action='workspace_created',
                    resource_type='workspace',
                    resource_id=workspace.id,
                    details={'workspace_name': workspace.name},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                response.update({
                    'result': 'success',
                    'message': _('Workspace created successfully'),
                    'records': WorkspaceSerializer(workspace, context={'request': request}).data
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def retrieve(self, request, *args, **kwargs):
        """Get workspace details"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            workspace = self.get_object()
            serializer = self.get_serializer(workspace, context={'request': request})
            
            response.update({
                'result': 'success',
                'message': _('Workspace details fetched successfully'),
                'records': serializer.data
            })
            
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def update(self, request, *args, **kwargs):
        """Update workspace"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            workspace = self.get_object()
            
            # Check permission
            member = WorkspaceMember.objects.get(workspace=workspace, user=request.user)
            if member.role not in ['owner', 'member']:
                response.update({
                    'result': 'failure',
                    'message': _('Permission denied')
                })
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(workspace, data=request.data, partial=True)
            if serializer.is_valid():
                old_name = workspace.name
                workspace = serializer.save()
                
                # Log the action
                AuditLog.objects.create(
                    workspace=workspace,
                    user=request.user,
                    action='workspace_updated',
                    resource_type='workspace',
                    resource_id=workspace.id,
                    details={
                        'old_name': old_name,
                        'new_name': workspace.name
                    },
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                response.update({
                    'result': 'success',
                    'message': _('Workspace updated successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except WorkspaceMember.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Not a member of this workspace')
            })
            status_code = status.HTTP_403_FORBIDDEN
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def destroy(self, request, *args, **kwargs):
        """Delete workspace"""
        response, status_code = {}, status.HTTP_200_OK
        
        try:
            workspace = self.get_object()
            
            # Check if user is owner
            member = WorkspaceMember.objects.get(workspace=workspace, user=request.user)
            if member.role != 'owner':
                response.update({
                    'result': 'failure',
                    'message': _('Only workspace owner can delete workspace')
                })
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
            workspace_name = workspace.name
            workspace.delete()
            
            response.update({
                'result': 'success',
                'message': _('Workspace deleted successfully')
            })
            
        except WorkspaceMember.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Not a member of this workspace')
            })
            status_code = status.HTTP_403_FORBIDDEN
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)


class WorkspaceMemberView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, WorkspacePermission]
    
    def get_serializer_class(self):
        serializer_mapping = {
            'list': WorkspaceMemberSerializer,
            'invite_member': InviteMemberSerializer,
            'update_role': UpdateMemberRoleSerializer,
        }
        return serializer_mapping.get(self.action, WorkspaceMemberSerializer)
    
    def list(self, request, *args, **kwargs):
        """List workspace members"""
        response, status_code = {}, status.HTTP_200_OK
        workspace_id = kwargs.get('workspace_id')
        
        try:
            workspace = get_object_or_404(Workspace, id=workspace_id)
            members = WorkspaceMember.objects.filter(workspace=workspace)
            serializer = self.get_serializer(members, many=True)
            
            response.update({
                'result': 'success',
                'message': _('Workspace members fetched successfully'),
                'records': serializer.data
            })
            
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def invite_member(self, request, *args, **kwargs):
        """Invite member to workspace"""
        response, status_code = {}, status.HTTP_200_OK
        workspace_id = kwargs.get('workspace_id')
        
        try:
            workspace = get_object_or_404(Workspace, id=workspace_id)
            
            # Check permission
            member = WorkspaceMember.objects.get(workspace=workspace, user=request.user)
            if member.role not in ['owner', 'member']:
                response.update({
                    'result': 'failure',
                    'message': _('Permission denied')
                })
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(
                data=request.data, 
                context={'workspace': workspace}
            )
            if serializer.is_valid():
                user = serializer.context['user']
                role = serializer.validated_data['role']
                
                # Create membership
                WorkspaceMember.objects.create(
                    workspace=workspace,
                    user=user,
                    role=role,
                    invited_by=request.user
                )
                
                # Log the action
                AuditLog.objects.create(
                    workspace=workspace,
                    user=request.user,
                    action='member_invited',
                    resource_type='workspace_member',
                    details={
                        'invited_user_email': user.email,
                        'role': role
                    },
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                response.update({
                    'result': 'success',
                    'message': _('Member invited successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except WorkspaceMember.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Not a member of this workspace')
            })
            status_code = status.HTTP_403_FORBIDDEN
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def update_role(self, request, *args, **kwargs):
        """Update member role"""
        response, status_code = {}, status.HTTP_200_OK
        workspace_id = kwargs.get('workspace_id')
        user_id = kwargs.get('user_id')
        
        try:
            workspace = get_object_or_404(Workspace, id=workspace_id)
            
            # Check if requester is owner
            requester_member = WorkspaceMember.objects.get(workspace=workspace, user=request.user)
            if requester_member.role != 'owner':
                response.update({
                    'result': 'failure',
                    'message': _('Only owners can update member roles')
                })
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
            # Get member to update
            member = get_object_or_404(WorkspaceMember, workspace=workspace, user_id=user_id)
            
            # Can't change owner role
            if member.role == 'owner':
                response.update({
                    'result': 'failure',
                    'message': _('Cannot change owner role')
                })
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                old_role = member.role
                member.role = serializer.validated_data['role']
                member.save()
                
                # Log the action
                AuditLog.objects.create(
                    workspace=workspace,
                    user=request.user,
                    action='member_role_updated',
                    resource_type='workspace_member',
                    resource_id=member.id,
                    details={
                        'user_email': member.user.email,
                        'old_role': old_role,
                        'new_role': member.role
                    },
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                response.update({
                    'result': 'success',
                    'message': _('Member role updated successfully')
                })
            else:
                response.update({
                    'result': 'failure',
                    'errors': {key: serializer.errors[key][0] for key in serializer.errors.keys()}
                })
                status_code = status.HTTP_400_BAD_REQUEST
                
        except WorkspaceMember.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Not a member of this workspace')
            })
            status_code = status.HTTP_403_FORBIDDEN
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)
    
    def remove_member(self, request, *args, **kwargs):
        """Remove member from workspace"""
        response, status_code = {}, status.HTTP_200_OK
        workspace_id = kwargs.get('workspace_id')
        user_id = kwargs.get('user_id')
        
        try:
            workspace = get_object_or_404(Workspace, id=workspace_id)
            
            # Check permission
            requester_member = WorkspaceMember.objects.get(workspace=workspace, user=request.user)
            if requester_member.role not in ['owner', 'member']:
                response.update({
                    'result': 'failure',
                    'message': _('Permission denied')
                })
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
            # Get member to remove
            member = get_object_or_404(WorkspaceMember, workspace=workspace, user_id=user_id)
            
            # Can't remove owner
            if member.role == 'owner':
                response.update({
                    'result': 'failure',
                    'message': _('Cannot remove workspace owner')
                })
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            # Log the action before deletion
            AuditLog.objects.create(
                workspace=workspace,
                user=request.user,
                action='member_removed',
                resource_type='workspace_member',
                details={
                    'removed_user_email': member.user.email,
                    'role': member.role
                },
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            member.delete()
            
            response.update({
                'result': 'success',
                'message': _('Member removed successfully')
            })
            
        except WorkspaceMember.DoesNotExist:
            response.update({
                'result': 'failure',
                'message': _('Not a member of this workspace')
            })
            status_code = status.HTTP_403_FORBIDDEN
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)


class AuditLogView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, WorkspacePermission]
    serializer_class = AuditLogSerializer
    
    def list(self, request, *args, **kwargs):
        """List audit logs for workspace"""
        response, status_code = {}, status.HTTP_200_OK
        workspace_id = kwargs.get('workspace_id')
        
        try:
            workspace = get_object_or_404(Workspace, id=workspace_id)
            audit_logs = AuditLog.objects.filter(workspace=workspace)
            serializer = self.get_serializer(audit_logs, many=True)
            
            response.update({
                'result': 'success',
                'message': _('Audit logs fetched successfully'),
                'records': serializer.data
            })
            
        except Exception as error:
            response.update({
                'result': 'failure',
                'message': _('Something went wrong'),
                'error': str(error)
            })
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response(response, status=status_code)