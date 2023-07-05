import secrets
from typing import Any

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_AUTHENTICATED = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_AUTHENTICATED,
         'Аутентифицированный пользователь'),
        (ROLE_ADMIN, 'Администратор'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_AUTHENTICATED,
    )
    name = models.CharField(max_length=100)
    family = models.CharField(max_length=100)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def save(self: 'User', *args: Any, **kwargs: Any) -> None:
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
        super().save(*args, **kwargs)
