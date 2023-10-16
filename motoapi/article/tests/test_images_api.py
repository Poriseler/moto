"""
Tests for Images API.
"""
from django.core.files import File
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image as Im
import os
import tempfile
from core.models import Image, Article
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from article.serializers import ArticleSerializer, ArticleDetailSerializer, ImageSerializer

IMAGES_URL = reverse('article:image-list')


def images_upload_url(article_id):
    """Created and returns and image upload URL."""
    return reverse('article:article-upload-thumbnail', args=[article_id])


def create_user(email='user@example.com', password='testpass123'):
    """Creates sample user."""
    return get_user_model().objects.create_user(email, password)


def create_article(user, **params):
    """Creates sample article."""
    default_payload = {
        'header': 'Test header',
        'lead': 'Test lead',
        'main_text': 'Test main text',
        'slug': 'test-header'
    }
    default_payload.update(params)

    return Article.objects.create(user=user, **default_payload)


def article_detail(article_id):
    """Creates and returns url to article details"""
    return reverse('article:article-detail', args=[article_id])


class PublicImageApiTests(TestCase):
    """Tests for unauthenticated requests to Image endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.article = create_article(user=self.user)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Im.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            self.image = Image.objects.create(
                article=self.article, photo=File(image_file))

    def test_displaying_list_images(self):
        """Tests displaying images list."""

        res = self.client.get(IMAGES_URL)
        images = Image.objects.all().order_by('-id')
        serializer = ImageSerializer(images, many=True)
        for image_obj in serializer.data:
            image_obj['photo'] = f'http://testserver{image_obj["photo"]}'

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_displaying_images_for_article(self):
        """Tests if only images for given article are retrieved."""

        article2 = create_article(user=self.user)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Im.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            self.image = Image.objects.create(
                article=article2, photo=File(image_file))
            self.image = Image.objects.create(
                article=article2, photo=File(image_file))

        res = self.client.get(IMAGES_URL, {'article-id': article2.id})
        images = Image.objects.filter(
            article__id__exact=article2.id).order_by('-id')
        serializer = ImageSerializer(images, many=True)
        for image_obj in serializer.data:
            image_obj['photo'] = f'http://testserver{image_obj["photo"]}'

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creating_images_not_allowed(self):
        """Tests if creating images is not allowed."""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Im.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            res = self.client.post(IMAGES_URL,
                                   {'article': self.article, 'photo': image_file}, format='multipart')

        self.assertEqual(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
