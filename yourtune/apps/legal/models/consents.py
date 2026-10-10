# apps/legal/models/consents.py

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel


class UserLegalConsent(UUIDModel):
    """
    Факт принятия пользователем конкретной версии
    юридического документа.
    """

    class ConsentSource(models.TextChoices):
        SIGNUP = "signup", _("Регистрация")
        SOCIAL_SIGNUP = "social_signup", _("Регистрация через соцсеть")
        LOGIN = "login", _("Вход")
        REQUIRED_REVIEW = "required_review", _("Обязательное ознакомление")
        SETTINGS = "settings", _("Настройки аккаунта")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="legal_consents",
        verbose_name=_("Пользователь"),
    )

    document_version = models.ForeignKey(
        "legal.LegalDocumentVersion",
        on_delete=models.CASCADE,
        related_name="consents",
        verbose_name=_("Версия документа"),
    )

    accepted_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Дата и время принятия"),
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP-адрес"),
    )

    user_agent = models.CharField(
        max_length=512,
        blank=True,
        default="",
        verbose_name=_("User-Agent"),
    )

    source = models.CharField(
        max_length=32,
        choices=ConsentSource.choices,
        default=ConsentSource.REQUIRED_REVIEW,
        verbose_name=_("Источник согласия"),
    )

    class Meta:
        verbose_name = _("Согласие пользователя")
        verbose_name_plural = _("Согласия пользователей")
        ordering = ["-accepted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "document_version"],
                name="unique_user_legal_document_consent",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "accepted_at"]),
            models.Index(fields=["document_version", "accepted_at"]),
        ]

    def __str__(self):
        return (
            f"{self.user} — {self.document_version} — "
            f"{self.accepted_at:%d.%m.%Y %H:%M}"
        )

    @property
    def document(self):
        """
        Удобный доступ к документу через выбранную версию.
        """
        return self.document_version.document

    @classmethod
    def has_accepted_version(cls, user, document_version):
        """
        Проверяет, принял ли пользователь конкретную версию.
        """
        if not user or not user.is_authenticated:
            return False

        return cls.objects.filter(
            user=user,
            document_version=document_version,
        ).exists()

    @classmethod
    def accept_version(
        cls,
        user,
        document_version,
        request=None,
        source=ConsentSource.REQUIRED_REVIEW,
    ):
        """
        Создаёт или возвращает согласие пользователя
        на конкретную версию документа.
        """
        ip_address = None
        user_agent = ""

        if request is not None:
            ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:512]

        consent, created = cls.objects.get_or_create(
            user=user,
            document_version=document_version,
            defaults={
                "accepted_at": timezone.now(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "source": source,
            },
        )

        return consent, created