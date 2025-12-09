from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.signin_url = reverse('signin')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'password_confirm': 'StrongPassword123!'
        }

    def test_registration(self):
        """
        Ensure we can register a new user.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_signin(self):
        """
        Ensure we can login with valid credentials.
        """
        # Create user first
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Verify user
        user = User.objects.get(email='test@example.com')
        user.is_verified = True
        user.save()
        
        # Try login
        login_data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.signin_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_signin_invalid_credentials(self):
        """
        Ensure login fails with invalid password.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.signin_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unique_email(self):
        """
        Ensure we cannot register two users with same email.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
