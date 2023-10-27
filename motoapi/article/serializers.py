"""
Serializers for article API.
"""
from rest_framework import serializers

from core.models import Article, Tag, Image


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag object."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article objects."""
    tags = TagSerializer(many=True, required=False, read_only=False)

    class Meta:
        model = Article
        fields = ['id', 'header', 'user', 'slug', 'tags', 'thumbnail']
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
