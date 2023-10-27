"""
Database models.
"""

from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify
from motoapi import settings
import os
import uuid
from core.custom_mixins import ResizeImageMixin


def thumbnail_file_path(instance, filename):
    """Generates file path for thumbnail."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}_thumbnail{ext}'

    return os.path.join('uploads', 'article', 'thumbnails', filename)


def image_file_path(instance, filename):
    """Generates file path for image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'article', filename)


class Tag(models.Model):
    """Tag object."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=False, blank=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('Email field is required.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Article(models.Model, ResizeImageMixin):
    """Article object."""
    CATEGORY_CHOICES = [
        ('newsy', 'Newsy'),
        ('felietony', 'Felietony'),
        ('relacje', 'Relacje'),
        ('testy', 'Testy')
    ]

    header = models.CharField(max_length=255)
    lead = models.TextField(max_length=500)
    main_text = models.TextField()
    slug = models.SlugField(blank=True, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL)
    tags = models.ManyToManyField('Tag')
    thumbnail = models.ImageField(
        null=True, blank=True, upload_to=thumbnail_file_path)
    category = models.CharField(
        max_length=255, choices=CATEGORY_CHOICES, default='newsy')
    photos_source = models.CharField(
        max_length=255, default='materiały producenta')

    def __str__(self) -> str:
        return self.header

    def save(self, *args, **kwargs):
        self.slug = slugify(self.header)
        if self.thumbnail and (self.thumbnail.width > 800 or self.thumbnail.height > 600):
            self.resize(self.thumbnail, (800, 600))
        return super().save(*args, **kwargs)


class Image(models.Model, ResizeImageMixin):
    """Image object."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=image_file_path)

    def save(self, *args, **kwargs):
        if self.pk is None and (self.photo.width > 1200 or self.photo.height > 800):
            self.resize(self.photo, (1200, 800))
        return super().save(*args, **kwargs)
