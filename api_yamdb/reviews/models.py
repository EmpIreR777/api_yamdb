from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    # title = models.ForeignKey(
    #     Title, on_delete=models.CASCADE,
    #     related_name='reviews',
    #     verbose_name='творчество'
    # )
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

    # class Meta:
    #     vebrose_name = 'Отзыв'
    #     vebrose_name_plural = 'Отзывы'
    #     ordering = ('-pub_date',)

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

    # class Meta:
    #     vebrose_name = 'Комментарий'
    #     vebrose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:40]
