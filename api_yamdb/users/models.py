from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(
        'Роль', max_length=20, choices=ROLE_CHOICES, default=USER
    )
    bio = models.TextField(
        'Биография', blank=True, null=True
    )

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
