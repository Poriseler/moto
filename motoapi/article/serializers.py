"""
Serializers for article API.
"""
from rest_framework import serializers

from core.models import Article, Tag, Image


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag object."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article objects."""
    tags = TagSerializer(many=True, required=False, read_only=False)

    class Meta:
        model = Article
        fields = ['id', 'header', 'user', 'slug', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, article):
        """Creates or gets already created tags."""
        for tag in tags:
            tag_obj, create = Tag.objects.get_or_create(**tag)
            article.tags.add(tag_obj)

    def create(self, validated_data):
        """Creating a recipe."""
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)

        if tags:
            self._get_or_create_tags(tags, article)

        return article

    def update(self, instance, validated_data):
        """Updating a recipe."""
        tags = validated_data.pop('tags', [])
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ArticleDetailSerializer(ArticleSerializer):
    """Serializer for Article details."""

    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + ['lead', 'main_text']
        read_only_fields = ArticleSerializer.Meta.read_only_fields + ['user']


class ArticleThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for Article thumbnail."""

    class Meta:
        model = Article
        fields = ['id', 'thumbnail']
        read_only_fields = ['id']
        extra_kwargs = {'thumbnail': {'required': 'True'}}


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for Image."""

    class Meta:
        model = Image
        fields = ['id', 'article', 'photo']
        read_only_fields = ['id',]
        extra_kwargs = {'photo': {'required': 'True'}}


# class ImageSerializer2(serializers.ModelSerializer):
#     """Serializer for Image."""

#     class Meta:
#         model = Image
#         fields = ['id', 'article', 'photo']
#         read_only_fields = ['id',]


# class MultiImageSerializer(serializers.Serializer):
#     """Serializer for Image."""
#     article = serializers.CharField()

#     def create(self, validated_data):
#         article_obj = Article.objects.get(id=validated_data.get('article'))

#         for photo in self.context['photos']:
#             Image.objects.create(article=article_obj, photo=photo)

#         return {'article': article_obj.id}


# class CustomImagesSerializer(serializers.Serializer):
#     article = serializers.ListField(
#         child=serializers.CharField()
#     )
#     photos = serializers.ListField(
#         child=serializers.ImageField()
#     )

#     def create(self, validated_data):
#         article_id = validated_data.get('article')[0]
#         article_obj = Article.objects.get(id=article_id)
#         created_photos = []
#         for photo_obj in validated_data.get('photos'):

#             img = Image.objects.create(article=article_obj, photo=photo_obj)
#             created_photos.append(photo_obj.name)

#         response = {'article': article_id, 'photos': created_photos}

#         return response


# class CustomImagesSerializer2(serializers.Serializer):
#     article = serializers.ListField(
#         child=serializers.CharField()
#     )
#     photos = serializers.ListField(
#         child=serializers.ImageField()
#     )

#     class Meta:
#         list_serializer_class = CustomImagesListSerializer

#     def create(self, validated_data):
#         article_id = validated_data.get('article')[0]
#         article_obj = Article.objects.get(id=article_id)
#         created_photos = []
#         for photo_obj in validated_data.get('photos'):

#             img = Image.objects.create(article=article_obj, photo=photo_obj)
#             created_photos.append(photo_obj.name)

#         response = {'article': article_id, 'photos': created_photos}

#         return response
