"""
Tests for article API. 
"""
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Article, Tag, Image

from PIL import Image as Im
import os
import tempfile
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from article.serializers import ArticleSerializer, ArticleDetailSerializer

ARTICLE_URL = reverse('article:article-list')


def thumbnail_upload_url(article_id):
    """Creates and returns and thumbnail upload URL."""
    return reverse('article:article-upload-thumbnail', args=[article_id])


def photos_upload_url(article_id):
    """Creates and returns images upload URL"""
    return reverse('article:article-upload-photos', args=[article_id])


def article_detail(article_id):
    """Creates and returns url to article details"""
    return reverse('article:article-detail', args=[article_id])


def create_article(user, **params):
    """Creates and returns sample article."""
    default_payload = {
        'header': 'Test header',
        'lead': 'Test lead',
        'main_text': 'Test main text',
        'slug': 'test-header'
    }
    default_payload.update(params)
    article = Article.objects.create(user=user, **default_payload)
    return article


def create_user(**params):
    """Creates and returns user."""
    return get_user_model().objects.create_user(**params)


class PublicArticleApiTests(TestCase):
    """Tests for unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieving_articles_list(self):
        """Tests retrieving list of articles for unathenticated users."""
        user = create_user(email='test@example.com', password='pass123')
        create_article(user=user)
        create_article(user=user, header='Test header2', slug='test-header2')

        res = self.client.get(ARTICLE_URL)

        articles = Article.objects.all().order_by('-id')
        serializer = ArticleSerializer(articles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_specific_article(self):
        """Tests retriving details of specific article."""
        user = create_user(email='test@example.com', password='pass123')
        article = create_article(user=user)
        url = article_detail(article.slug)
        res = self.client.get(url)

        serializer = ArticleDetailSerializer(article)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creating_article_unauthorized(self):
        """Tests raising error while creating article unauthorized."""
        payload = {
            'header': 'Test header',
            'lead': 'Test lead',
            'main_text': 'Test main text',
            'slug': 'test-header'
        }
        res = self.client.post(ARTICLE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_article_unauthorized(self):
        """Tests raising error while updating article unathorized."""
        payload = {
            'main_text': 'Test changed main text',
        }
        res = self.client.post(ARTICLE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_articles_by_tag(self):
        """Tests returning only articles associated with given tags."""
        tag1 = Tag.objects.create(name='Test tag', slug='test-tag')
        tag2 = Tag.objects.create(name='Test tag2', slug='test-tag2')
        user = create_user(email='user@example.com', password='pass123')
        payload = {
            'lead': 'Test lead2',
            'main_text': 'Test main text2'
        }
        payload2 = {
            'header': 'Test header3',
            'slug': 'test-header3'
        }
        article1 = create_article(user=user)
        article2 = create_article(user=user, **payload)
        article3 = create_article(user=user, **payload2)
        article1.tags.add(tag1)
        article2.tags.add(tag2)
        article3.tags.add(tag2)

        params = {'tag': f'{tag2.slug}'}

        serialized_article1 = ArticleSerializer(article1)
        serialized_article2 = ArticleSerializer(article2)
        serialized_article3 = ArticleSerializer(article3)

        res = self.client.get(ARTICLE_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(serialized_article1.data, res.data)
        self.assertIn(serialized_article2.data, res.data)
        self.assertIn(serialized_article3.data, res.data)

    def test_search_article_by_one_word_query(self):
        """Tests searching articles containing given string with one word."""
        payload1 = {'header': 'Test header', 'slug': 'test-header'}
        payload2 = {'header': 'Example header', 'slug': 'example-header'}
        payload3 = {'header': 'Mock name', 'slug': 'mock-name'}
        user = create_user(email='user@example.com', password='pass123')
        article1 = create_article(user=user, **payload1)
        article2 = create_article(user=user, **payload2)
        article3 = create_article(user=user, **payload3)
        params = {'query': 'header'}
        res = self.client.get(ARTICLE_URL, params)

        serialized_article1 = ArticleSerializer(article1)
        serialized_article2 = ArticleSerializer(article2)
        serialized_article3 = ArticleSerializer(article3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serialized_article1.data, res.data)
        self.assertIn(serialized_article2.data, res.data)
        self.assertNotIn(serialized_article3.data, res.data)

    def test_search_article_by_multi_word_query(self):
        """Tests searching articles containing given string with at least two words."""
        payload1 = {'header': 'Test header', 'slug': 'test-header'}
        payload2 = {'header': 'test header with example',
                    'slug': 'test-header-with-example'}
        payload3 = {'header': 'Mock name', 'slug': 'mock-name'}
        user = create_user(email='user@example.com', password='pass123')
        article1 = create_article(user=user, **payload1)
        article2 = create_article(user=user, **payload2)
        article3 = create_article(user=user, **payload3)
        params = {'query': 'test header'}
        res = self.client.get(ARTICLE_URL, params)

        serialized_article1 = ArticleSerializer(article1)
        serialized_article2 = ArticleSerializer(article2)
        serialized_article3 = ArticleSerializer(article3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serialized_article1.data, res.data)
        self.assertIn(serialized_article2.data, res.data)
        self.assertNotIn(serialized_article3.data, res.data)

    def test_upload_images_unauthorized_error(self):
        """Tests uploading images to article by anonymous user."""
        user = create_user(email='user@example.com', password='testpass123')
        article = create_article(user=user)
        url = photos_upload_url(article.slug)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Im.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            res = self.client.post(url,
                                   {'article': self.article.slug, 'photo': image_file}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateArticleApiTests(TestCase):
    """Tests for authenticated requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@example.com", password='pass123')
        self.client.force_authenticate(self.user)

    def test_create_article_success(self):
        """Tests creation of article by uthenticated user."""
        payload = {
            'header': 'Test header',
            'lead': 'Test lead',
            'main_text': 'Test main text',
            'slug': 'test-header'
        }

        res = self.client.post(ARTICLE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        article = Article.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(article, k), v)
        self.assertEqual(article.user, self.user)

    def test_update_article_success(self):
        """Tests updating article by authenticated user."""
        article = create_article(user=self.user)
        payload = {
            'main_text': 'Test changed main text'
        }
        url = article_detail(article.slug)
        res = self.client.patch(url, payload)
        article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(article, k), v)

    def test_unable_to_change_user_associated_with_article(self):
        """Tests if changing user assigned to article is ignored by serializer."""
        new_user = create_user(email="user2@example.com", password='pass123')
        article = create_article(user=self.user)
        url = article_detail(article.slug)
        payload = {'user': new_user.id}

        self.client.patch(url, payload)
        article.refresh_from_db()

        self.assertEqual(article.user, self.user)

    def test_delete_another_user_article(self):
        """Tests if deleting another user article raises error."""
        new_user = create_user(email="user2@example.com", password='pass123')
        article = create_article(user=new_user)
        url = article_detail(article.slug)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        articles = Article.objects.filter(id=article.id)
        self.assertTrue(articles.exists())

    def test_updating_another_user_article(self):
        """Tests if updating another user article raises error."""
        new_user = create_user(email="user2@example.com", password='pass123')
        article = create_article(user=new_user)
        payload = {
            'lead': 'Test lead changed',
            'main_text': 'Main text changed'
        }
        url = article_detail(article.slug)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        article.refresh_from_db()

        for k, v in payload.items():
            self.assertNotEqual(getattr(article, k), v)

    def test_create_article_with_new_tags(self):
        """Tests creating article with new tags."""
        payload = {
            'header': 'Test header',
            'lead': 'Test lead',
            'main_text': 'Test main text',
            'slug': 'test-header',
            'tags': [
                {
                    'name': 'Test tag',
                    'slug': 'test-tag'
                },
                {
                    'name': 'Test tag2',
                    'slug': 'test-tag2'
                }
            ],
        }
        res = self.client.post(ARTICLE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        articles = Article.objects.all()
        self.assertEqual(articles.count(), 1)

        article = articles[0]
        self.assertEqual(article.tags.count(), 2)

        for tag in payload['tags']:
            exists = article.tags.filter(name=tag['name']).exists()
            self.assertTrue(exists)

    def test_create_article_with_exisiting_tags(self):
        """Tests creating article when tags already exists."""
        tag1 = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )

        payload = {
            'header': 'Test header',
            'lead': 'Test lead',
            'main_text': 'Test main text',
            'slug': 'test-header',
            'tags': [
                {
                    'name': 'Test tag',
                    'slug': 'test-tag'
                },
                {
                    'name': 'Test tag2',
                    'slug': 'test-tag2'
                }
            ],
        }
        res = self.client.post(ARTICLE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        articles = Article.objects.all()
        self.assertEqual(articles.count(), 1)

        article = articles[0]
        self.assertEqual(article.tags.count(), 2)
        self.assertIn(tag1, article.tags.all())

        for tag in payload['tags']:
            exists = article.tags.filter(name=tag['name']).exists()
            self.assertTrue(exists)

    def test_create_tag_on_article_update(self):
        """Tests updating article with previously non existing tag."""
        article = create_article(user=self.user)
        payload = {'tags': [
            {
                'name': 'Test tag',
                'slug': 'test-tag'
            }
        ]}
        url = article_detail(article.slug)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(slug='test-tag')
        self.assertIn(new_tag, article.tags.all())

    def test_assign_tag_on_article_update(self):
        """Tests adding already created tag to an article on update."""
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )
        payload = {'tags': [
            {
                'name': 'Test tag',
                'slug': 'test-tag'
            }
        ]}
        article = create_article(user=self.user)

        url = article_detail(article.slug)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        article.refresh_from_db()
        self.assertIn(tag, article.tags.all())
        tags = Tag.objects.filter(name=tag.name)
        self.assertEqual(tags.count(), 1)

    def test_remove_tags_from_article(self):
        """Tests removing tags from article on update."""
        article = create_article(user=self.user)
        tag = Tag.objects.create(
            name='Test tag',
            slug='test-tag'
        )
        article.tags.add(tag)

        payload = {'tags': []}

        url = article_detail(article.slug)
        res = self.client.patch(url, payload, format='json')
        article.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(article.tags.count(), 0)


class ThumbnailUploadTests(TestCase):
    """Tests for uploading thumbnail to article."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='pass123')
        self.client.force_authenticate(self.user)
        self.article = create_article(user=self.user)

    def tearDown(self) -> None:
        self.article.thumbnail.delete()

    def test_upload_thumbnail(self):
        """Tests uploading thumbnail to article"""

        url = thumbnail_upload_url(self.article.slug)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Im.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'thumbnail': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('thumbnail', res.data)
        self.assertTrue(os.path.exists(self.article.thumbnail.path))

    def test_upload_thumbnail_bad_request(self):
        """Tests uploading invalid thumbnail."""

        url = thumbnail_upload_url(self.article.slug)
        payload = {'thumbnail': 'not_img'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_images_success(self):
        """Tests uploading new images to article."""
        url = photos_upload_url(self.article.slug)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Im.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            res = self.client.post(url,
                                   {'article': self.article.slug, 'photo': image_file}, format='multipart')

        images = Image.objects.filter(article__slug__exact=self.article.slug)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(images.count(), 1)

    def test_upload_images_bad_request(self):
        """Tests uploading invalid image."""
        url = photos_upload_url(self.article.slug)
        res = self.client.post(
            url, {'article': self.article.slug, 'photo': 'NotAPhoto'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
