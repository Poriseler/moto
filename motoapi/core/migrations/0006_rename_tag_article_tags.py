# Generated by Django 4.2.6 on 2023-10-11 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_article_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='tag',
            new_name='tags',
        ),
    ]
