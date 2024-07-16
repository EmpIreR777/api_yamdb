from django.db import models
from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator


class BaseCategoryGenreModel(models.Model):
    """Базовая модель для категорий и жанров."""
    name = models.CharField(
        'Название', max_length=256
    )
    slug = models.SlugField(
        'Слаг', max_length=50, unique=True
    )

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


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='творчество'
    )
    text = models.CharField(
        max_length=200
    )
    # author = models.ForeignKey(
    #     User, on_delete=models.CASCADE,
    #     related_name='reviews',
    #     verbose_name='автор'
    # )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(1), MaxValueValidator(10)),
        error_messages={'validators': 'от 1 до 10'}
    )
    pub_data = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        vebrose_name = 'Отзыв'
        vebrose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:40]


class Comment(models.Model):
    riview = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.CharField(
        max_length=200
    )
    # author = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='comments',
    #     verbose_name='автор'
    # )
    pub_data = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        vebrose_name = 'Комментарий'
        vebrose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:40]
