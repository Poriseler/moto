"""
Tests for article API. 
"""
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Article, Tag

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from article.serializers import ArticleSerializer, ArticleDetailSerializer

ARTICLE_URL = reverse('article:article-list')


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
        url = article_detail(article.id)
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
        url = article_detail(article.id)
        res = self.client.patch(url, payload)
        article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(article, k), v)

    def test_unable_to_change_user_associated_with_article(self):
        """Tests if changing user assigned to article is ignored by serializer."""
        new_user = create_user(email="user2@example.com", password='pass123')
        article = create_article(user=self.user)
        url = article_detail(article.id)
        payload = {'user': new_user.id}

        self.client.patch(url, payload)
        article.refresh_from_db()

        self.assertEqual(article.user, self.user)

    def test_delete_another_user_article(self):
        """Tests if deleting another user article raises error."""
        new_user = create_user(email="user2@example.com", password='pass123')
        article = create_article(user=new_user)
        url = article_detail(article.id)
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
        url = article_detail(article.id)
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
        url = article_detail(article.id)
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

        url = article_detail(article.id)
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

        url = article_detail(article.id)
        res = self.client.patch(url, payload, format='json')
        article.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(article.tags.count(), 0)
