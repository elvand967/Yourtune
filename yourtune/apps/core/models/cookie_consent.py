
# apps/core/models/cookie_consent.py

from django.conf import settings
from django.db import models


class CookieConsent(models.Model):
    """
    Журнал решений пользователя относительно использования cookie.

    Модель хранит факт согласия, выбранные категории,
    версию политики и технический контекст.
    """

    class ConsentSource(models.TextChoices):
        BANNER = "banner", "Баннер"
        SETTINGS = "settings", "Настройки cookie"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cookie_consents",
        verbose_name="Пользователь",
    )

    session_key = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Ключ сессии",
    )

    necessary = models.BooleanField(
        default=True,
        verbose_name="Необходимые cookie",
    )

    analytics = models.BooleanField(
        default=False,
        verbose_name="Аналитические cookie",
    )

    marketing = models.BooleanField(
        default=False,
        verbose_name="Маркетинговые cookie",
    )

    policy_version = models.CharField(
        max_length=20,
        verbose_name="Версия политики",
    )

    source = models.CharField(
        max_length=20,
        choices=ConsentSource.choices,
        default=ConsentSource.BANNER,
        verbose_name="Источник решения",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP-адрес",
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name="Браузер и устройство",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата согласия",
    )

    class Meta:
        verbose_name = "Согласие на cookie"
        verbose_name_plural = "Согласия на cookie"
        ordering = ["-created_at"]

    def __str__(self):
        user = self.user.email if self.user else "Анонимный посетитель"
        return f"{user} — {self.created_at:%d.%m.%Y %H:%M}"