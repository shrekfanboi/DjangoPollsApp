# Generated by Django 4.1 on 2024-06-16 15:50

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0013_user_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='content',
            field=markdownx.models.MarkdownxField(blank=True, help_text='Markdown is supported.'),
        ),
    ]