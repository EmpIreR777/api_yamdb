from datetime import datetime

from django.core.validators import MaxValueValidator
from django.db import models


class BaseCategoryGenreModel(models.Model):
    """Базовая модель для категорий и жанров."""
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Category(BaseCategoryGenreModel):
    """Модель категорий произведения."""

    class Meta:
        vebrose_name = 'Категория'
        vebrose_name_plural = 'Категории'


class Genre(BaseCategoryGenreModel):
    """Модель жанров произведения."""

    class Meta:
        vebrose_name = 'Жанр'
        vebrose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField('Название', max_length=256)
    year = models.IntegerField(
        'Год выпуска',
        validators=[
            MaxValueValidator(
                datetime.now().year,
                'Год выпуска не может быть больше текущего'
            )
        ]
    )
    description = models.TextField('Описание', null=True, blank=True)
    genre = models.ManyToManyField(
        Genre,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        vebrose_name = 'Произведение'
        vebrose_name_plural = 'Произведения'
        ordering = ('year',)

    def __str__(self):
        return self.name
