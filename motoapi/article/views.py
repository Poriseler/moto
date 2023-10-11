"""
Views for article API.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.custom_permissions import IsOwnerOrReadOnly
from core.models import Article, Tag
from article import serializers


class ArticleViewSet(viewsets.ModelViewSet):
    """View for manage article API."""
    serializer_class = serializers.ArticleDetailSerializer
    queryset = Article.objects.all().order_by('-id')
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        """Returns serializer class for request."""

        if self.action == 'list':
            return serializers.ArticleSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new article."""
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """View for manage tags API."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all().order_by('-id')
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]
