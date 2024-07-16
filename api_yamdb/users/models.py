from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)
    bio = models.TextField(blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
