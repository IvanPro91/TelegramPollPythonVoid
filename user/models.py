from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    token = models.CharField(max_length=20, null=True, verbose_name="Токен пользователя")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
