
# apps/users/models/social_account.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import UUIDModel


class SocialAccount(UUIDModel):
    class Provider(models.TextChoices):
        GOOGLE = "google", _("Google")
        GITHUB = "github", _("GitHub")
        YANDEX = "yandex", _("Yandex")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_accounts",
        verbose_name=_("Пользователь"),
    )
    provider = models.CharField(max_length=20, choices=Provider.choices, verbose_name=_("Провайдер"))
    provider_uid = models.CharField(max_length=255, verbose_name=_("UID провайдера"))
    email = models.EmailField(blank=True, default="", verbose_name=_("Email"))
    extra_data = models.JSONField(default=dict, blank=True, verbose_name=_("Доп. данные"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Основной аккаунт"))

    class Meta:
        verbose_name = _("Социальный аккаунт")
        verbose_name_plural = _("Социальные аккаунты")
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_uid"],
                name="uniq_social_provider_uid",
            ),
        ]