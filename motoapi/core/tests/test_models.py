"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Article, Tag


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test if creating custom user is successful."""
        email = "user@example.com"
        password = 'testpwd123'
        user = get_user_model().objects.create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_superuser(self):
        """Tests if creating custom superuser is successful."""
        email = "admin@example.com"
        password = "testpass123"

        super_user = get_user_model().objects.create_superuser(email, password)
        self.assertEqual(super_user.email, email)
        self.assertTrue(super_user.check_password(password))
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_staff)

    def test_normalize_email_when_signup(self):
        """Tests if email is normalized during signup."""
        test_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        password = "testpass123"

        for email, expected_email in test_emails:
            user = get_user_model().objects.create_user(email, password)
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Tests if creating user without email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_create_article(self):
        """Tests creation of article."""
        user = get_user_model().objects.create(
            email='user@example.com', password='pass123')
        article = Article.objects.create(
            header='Test article',
            slug='test-article',
            lead='Test lead',
            main_text='Test main text',
            user=user
        )
        self.assertEqual(str(article), article.header)

    def test_create_tag(self):
        """Tests creation of tag."""
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )

        self.assertEqual(str(tag), tag.name)
