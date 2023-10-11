"""
URL mappings for article app.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from article import views

router = DefaultRouter()
router.register('recipes', views.ArticleViewSet)
router.register('tags', views.TagViewSet)

app_name = 'article'

urlpatterns = [
    path('', include(router.urls))
]
