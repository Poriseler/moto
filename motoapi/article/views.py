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

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new article."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Returns articles and filters for tags if specified as parameter."""
        tag = self.request.query_params.get('tag')
        query = self.request.query_params.get('query')
        queryset = self.queryset
        if tag:
            queryset = queryset.filter(tags__slug__icontains=tag)
        if query:
            queryset = queryset.filter(header__icontains=query)
        return queryset.order_by('-id')

    @action(methods=['POST'], detail=True, url_path='upload-thumbnail')
    def upload_thumbnail(self, request, slug=None):
        """Upload image to article."""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)


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


class ImagesViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ImageSerializer
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]


    def get_serializer_class(self):
        """Returns serializer class for request."""

        if self.action == 'multi_upload':
            return serializers.MultiImageSerializer

        return self.serializer_class

    def get_queryset(self):
        article_id = self.request.query_params.get('article_id')
        queryset = self.queryset
        if article_id:
            return queryset.filter(article__id__exact=article_id)
        return queryset.order_by('-id')

    @action(methods=['POST'], detail=False, url_path='multi-upload')
    def multi_upload(self, request, *args, **kwargs):
        photos = request.FILES.getlist('photo', None)

        data = { 'article' : request.POST.get('article', None)}

        serializer = self.get_serializer(data=data, context={'photos':photos})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



# class ImagesUploadView(generics.CreateAPIView):
class ImagesUploadView(generics.ListCreateAPIView):

    parser_classes = [FormParser, MultiPartParser]
    serializer_class = serializers.CustomImagesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]
    queryset = Image.objects.all()

    def get_serializer_class(self):

        if self.request.method=='GET':
            return serializers.ImageSerializer
        return self.serializer_class

    def get_queryset(self):
        article_id = self.request.query_params.get('article_id')
        queryset = self.queryset
        if article_id:
            return queryset.filter(article__id__exact=article_id)
        return queryset.order_by('-id')

