# Generated by Django 3.2 on 2024-07-19 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_review_title_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Описание'),
        ),
    ]
