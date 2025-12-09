from django.utils.text import slugify
from rest_framework import serializers
from apps.workspaces.models import Workspace, WorkspaceMember, AuditLog
from apps.authentication.models import User

# Avoid circular import - define inline
class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class WorkspaceSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'slug', 'role', 'member_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                member = WorkspaceMember.objects.get(workspace=obj, user=request.user)
                return member.role
            except WorkspaceMember.DoesNotExist:
                return None
        return None
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Generate unique slug
        base_slug = slugify(validated_data['name'])
        slug = base_slug
        counter = 1
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        workspace = Workspace.objects.create(
            owner=user,
            slug=slug,
            **validated_data
        )
        
        # Add owner as member
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role='owner'
        )
        
        return workspace


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'role', 'invited_by', 'joined_at']
        read_only_fields = ['id', 'user', 'invited_by', 'joined_at']


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['member', 'viewer'])
    
    def validate_email(self, value):
        workspace = self.context['workspace']
        
        # Check if user exists
        from apps.authentication.models import User
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')
        
        # Check if already a member
        if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            raise serializers.ValidationError('User is already a member of this workspace')
        
        self.context['user'] = user
        return value


class UpdateMemberRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['member', 'viewer'])


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'resource_type', 'resource_id', 'details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']