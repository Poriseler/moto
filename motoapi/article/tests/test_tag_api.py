"""
Tests for tags API.
"""
from core.models import Tag, Article

from article.serializers import TagSerializer

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('article:tag-list')


def detail_url(tag_id):
    """Creates and return detail url for a tag."""
    return reverse('article:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='pass123'):
    """Creates and returns user."""
    return get_user_model().objects.create(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Tests for unauthenticated requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_tags(self):
        """Tests retrieving all tags."""
        Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )
        Tag.objects.create(
            name='Test tag2',
            slug='test-tag2'
        )

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-id')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_unauthenticated(self):
        payload = {
            'name': 'Test tag',
            'slug': 'test-tag'
        }
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_tag_unauthenticated(self):
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )
        payload = {
            'name': 'Test tag2',
            'slug': 'test-tag2'
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_tag_unauthenticated(self):
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )

        url = detail_url(tag.id)
        res = self.client.delete(url)

        tags = Tag.objects.filter(id=tag.id)

        self.assertTrue(tags.exists())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicTagsApiTests(TestCase):
    """Tests for authenticated requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_create_tag_successful(self):
        """Tests creating tag by authenticated user."""
        payload = {
            'name': 'Test tag',
            'slug': 'test-tag'
        }
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_tag_successful(self):
        """Tests updating tag for authenticated user."""
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )
        payload = {
            'name': 'Test tag2',
            'slug': 'test-tag2'
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(tag, k), v)

    def test_delete_tag_successful(self):
        """Tests deleting a tag by authenticated user."""
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tags = Tag.objects.filter(id=tag.id)
        self.assertFalse(tags.exists())

    