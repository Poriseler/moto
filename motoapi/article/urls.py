"""
URL mappings for article app.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from article import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet)
router.register('tags', views.TagViewSet)
router.register('images', views.ImagesViewSet)

app_name = 'article'

urlpatterns = [
    path('', include(router.urls))
]
