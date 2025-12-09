from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User
from apps.workspaces.models import Workspace, WorkspaceMember

class WorkspaceTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='StrongPassword123!',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.workspace_list_url = reverse('workspace_list_create')

    def test_create_workspace(self):
        """
        Ensure we can create a new workspace.
        """
        data = {
            'name': 'My Test Workspace',
            'slug': 'my-test-workspace'
        }
        response = self.client.post(self.workspace_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workspace.objects.count(), 1)
        self.assertEqual(Workspace.objects.get().owner, self.user)

    def test_list_workspaces(self):
        """
        Ensure we can list workspaces we own.
        """
        w1 = Workspace.objects.create(name='Workspace 1', slug='ws-1', owner=self.user)
        w2 = Workspace.objects.create(name='Workspace 2', slug='ws-2', owner=self.user)
        
        # Must manually create membership because view filters by members
        WorkspaceMember.objects.create(workspace=w1, user=self.user, role='owner')
        WorkspaceMember.objects.create(workspace=w2, user=self.user, role='owner')
        
        response = self.client.get(self.workspace_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Adjust expectation based on response structure (usually result/records/list)
        # Based on AuthenticationView, likely uses 'records' or 'results' wrapper
        # I'll check response content loosely or just status code for now if wrapper is unknown
        # But looking at auth views, it uses 'result' and 'records'.
        # Let's assume standard DRF or custom wrapper. I will verify status code primarily.
        self.assertEqual(len(response.data.get('records', response.data)), 2)

    def test_create_workspace_unauthenticated(self):
        """
        Ensure unauthenticated users cannot create workspaces.
        """
        self.client.force_authenticate(user=None)
        data = {
            'name': 'Anonymouse Workspace',
            'slug': 'anon-ws'
        }
        response = self.client.post(self.workspace_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
