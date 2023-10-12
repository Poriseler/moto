"""
Tests for the Django admin site.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from rest_framework import status
from core.models import Article, Tag, Image as Im

from PIL import Image
import tempfile

CREATE_USER_URL = reverse('admin:core_user_add')
CREATE_ARTICLE_URL = reverse('admin:core_article_add')
CREATE_TAG_URL = reverse('admin:core_tag_add')
CREATE_IMAGE_URL = reverse('admin:core_image_add')


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@example.com',
            'testpass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
            name='Test',
            surname='Usersky'
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.surname)
        self.assertContains(res, self.user.email)

    def test_user_edit_page(self):
        """Tests that user edit page is opening correctly."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_create_page(self):
        """Tests that page for creating new users is opening correctly."""
        res = self.client.get(CREATE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_article_create_page(self):
        """Tests that page for creating new articles opens correctly."""
        res = self.client.get(CREATE_ARTICLE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_article_update_page(self):
        """Tests that page for updating article opens correctly."""
        article = Article.objects.create(
            header='Test header',
            lead='Test lead',
            main_text='Main text',
            slug='test-header',
            user=self.user
        )
        url = reverse('admin:core_article_change', args=[article.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tag_create_page(self):
        """Tests that page for creating tags opens correctly"""
        res = self.client.get(CREATE_TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tag_update_page(self):
        """Tests that page for updating tag opens correctly"""
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-slug'
        )
        url = reverse('admin:core_tag_change', args=[tag.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tag_image_page(self):
        """Tests that page for creating images opens correctly"""
        res = self.client.get(CREATE_IMAGE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # def test_image_update_page(self):
    #     """Tests that page for updating images opens correctly"""
    #     article = Article.objects.create(
    #         header='Test header',
    #         lead='Test lead',
    #         main_text='Main text',
    #         slug='test-header',
    #         user=self.user
    #     )

    #     with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
    #         img = Image.new('RGB', (10, 10))
    #         img.save(image_file, format='JPEG')
    #         image_file.seek(0)
    #         photo = Im.objects.create(
    #             photo=image_file,
    #             article=article
    #         )
    #     url = reverse('admin:core_image_change', args=[1])
    #     res = self.client.get(url)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
