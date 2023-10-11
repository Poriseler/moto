"""
Tests for user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

PROFILE_URL = reverse('user:profile')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Helper function for creating user."""
    user = get_user_model().objects.create_user(**params)
    return user


class PublicUserApiTests(TestCase):
    """Tests for unauthenticated users."""

    def setUp(self):
        self.client = APIClient()

    def test_creating_token_for_user(self):
        """Tests generating tokens for valid users."""
        email = 'user@example.com'
        password = 'testpass123'
        user = create_user(email=email, password=password)
        payload = {
            'email': email,
            'password': password
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_raising_error_when_bad_credentials(self):
        """Tests raising error when credentials are not valid."""
        email = "user@example.com"
        password = "testpass123"
        bad_password = "badpass123"
        user = create_user(email=email, password=password)
        payload = {
            'email': email,
            'passord': bad_password
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raising_error_when_blank_password(self):
        """Tests raising error when passowrd is not passed."""
        email = "user@example.com"
        password = "testpass123"
        user = create_user(email=email, password=password)
        payload = {
            'email': email,
            'passord': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raising_error_when_blank_username(self):
        """Tests raising error when username is not passed."""
        email = "user@example.com"
        password = "testpass123"
        user = create_user(email=email, password=password)
        payload = {
            'email': '',
            'passord': password
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """Tests for authenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',
                                password='pass123', name='Test', surname='Userowsky')
        self.client.force_authenticate(self.user)

    def test_retrive_profile_success(self):
        """Tests retrieving profile for authenticated user."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': 'user@example.com',
            'name': 'Test',
            'surname': 'Userowsky'
        })

    def test_update_user_profile(self):
        """Tests updating user profile."""
        payload = {
            'name': 'TestChanged',
            'password': 'newpass123'
        }
        res = self.client.patch(PROFILE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_post_not_allowed(self):
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
