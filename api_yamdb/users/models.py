from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_not_me


class CustomUser(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_not_me],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(unique=True, max_length=254)
    role = models.CharField(
        'Роль', max_length=20, choices=ROLE_CHOICES, default=USER
    )
    bio = models.TextField(
        'Биография', blank=True, null=True
    )
    confirmation_code = models.CharField(max_length=10, blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ['username']
