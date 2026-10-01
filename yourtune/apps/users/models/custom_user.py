# apps/users/models/custom_user.py
# =====================================

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from apps.core.models import UUIDModel
from apps.users.utils.managers import CustomUserManager


class CustomUser(UUIDModel, AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя для проекта yourtune.
    - email как основной идентификатор входа.
    - UUID в качестве primary key.
    - Поддержка Django auth (PermissionsMixin).
    """
    email = models.EmailField(unique=True, verbose_name="Email", db_index=True)
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")

    is_staff = models.BooleanField(default=False, verbose_name="Доступ в админку")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_verified = models.BooleanField(default=False, verbose_name="Email подтвержден")

    # Стандартные поля Django auth для совместимости
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    last_login = models.DateTimeField(blank=True, null=True, verbose_name="Последний вход")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        full_name = " ".join(
            part for part in [self.first_name, self.middle_name, self.last_name] if part
        ).strip()
        return full_name or self.email

    def get_full_name(self):
        return " ".join(
            part for part in [self.first_name, self.middle_name, self.last_name] if part
        ).strip()

    def get_short_name(self):
        return self.first_name or self.email