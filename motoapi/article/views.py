"""
Views for article API.
"""

from rest_framework import viewsets, status, generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from core.custom_permissions import IsOwnerOrReadOnly
from core.models import Article, Tag, Image
from article import serializers


class ArticleViewSet(viewsets.ModelViewSet):
    """View for manage article API."""
    serializer_class = serializers.ArticleDetailSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Returns serializer class for request."""

        if self.action == 'list':
            return serializers.ArticleSerializer
        if self.action == 'upload_thumbnail':
            return serializers.ArticleThumbnailSerializer
        if self.action == 'upload_photos':
            return serializers.ImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new article."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Returns articles and filters for tags if specified as parameter."""
        tag = self.request.query_params.get('tag')
        query = self.request.query_params.get('query')
        limit = self.request.query_params.get('limit')
        category = self.request.query_params.get('category')
        queryset = self.queryset
        if tag:
            queryset = queryset.filter(tags__slug__icontains=tag)
        if query:
            queryset = queryset.filter(header__icontains=query)
        if category:
            queryset = queryset.filter(category__iexact=category)
        queryset = queryset.order_by('-id')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset



    @action(methods=['POST'], detail=True, url_path='upload-thumbnail')
    def upload_thumbnail(self, request, slug=None):
        """Upload image to article."""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='upload-photos')
    def upload_photos(self, request, slug=None):
        article = self.get_object()
        data = [{'photo': photo, 'article': article.id}
                for photo in request.data.getlist('photo')]
        
        serializer = self.get_serializer(data=data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    """View for manage tags API."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all().order_by('-id')
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]


class ImagesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ImageSerializer
    queryset = Image.objects.all().order_by('-id')

    def get_queryset(self):
        queryset = self.queryset
        article_id = self.request.query_params.get('article-id', None)
        if article_id:
            # print(article_id)
            return queryset.filter(article__id__exact=article_id).order_by('-id')
        return queryset

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     print(queryset)
    #     serializer = serializers.ImageSerializer(
    #         data=list(queryset), many=True)
    #     if serializer.is_valid():
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
