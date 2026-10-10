# apps/legal/models/documents.py

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import UUIDModel


class LegalDocument(UUIDModel):
    """
    Юридический документ проекта.

    Примеры:
    - Политика конфиденциальности;
    - Правила использования сервиса;
    - Cookie-политика.
    """

    class DocumentType(models.TextChoices):
        PRIVACY_POLICY = "privacy_policy", _("Политика конфиденциальности")
        TERMS_OF_USE = "terms_of_use", _("Правила использования сервиса")

    document_type = models.CharField(
        max_length=32,
        choices=DocumentType.choices,
        unique=True,
        verbose_name=_("Тип документа"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Название документа"),
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("URL-идентификатор"),
        help_text=_(
            "Используется в публичных ссылках, "
            "например: privacy-policy."
        ),
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Краткое описание"),
        help_text=_(
            "Используется для SEO и краткого пояснения на странице."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
        help_text=_(
            "Неактивный документ не требуется принимать пользователям."
        ),
    )

    is_required = models.BooleanField(
        default=True,
        verbose_name=_("Обязателен для принятия"),
        help_text=_(
            "Обязательный документ блокирует доступ к защищённым разделам "
            "до принятия его актуальной версии."
        ),
    )

    current_version = models.ForeignKey(
        "legal.LegalDocumentVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="document_current_for",
        verbose_name=_("Актуальная версия"),
    )

    class Meta:
        verbose_name = _("Юридический документ")
        verbose_name_plural = _("Юридические документы")
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_current_version(self):
        """
        Возвращает актуальную версию документа.
        """
        return self.current_version


class LegalDocumentVersion(UUIDModel):
    """
    Конкретная редакция юридического документа.

    Каждое существенное изменение условий сервиса
    должно создаваться как новая версия.

    Это позволяет точно определить,
    какой текст принял пользователь.
    """

    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Документ"),
    )

    version = models.CharField(
        max_length=32,
        verbose_name=_("Версия"),
        help_text=_("Например: 1.0, 1.1, 2.0."),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок версии"),
    )

    content = CKEditor5Field(
        config_name="legal",
        verbose_name=_("Содержание документа"),
        help_text=_(
            "Отформатируйте текст с помощью визуального редактора. "
            "Можно вставить текст из Word или Google Docs."
        ),
    )

    summary = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Краткое описание изменений"),
        help_text=_(
            "Коротко опишите, что изменилось "
            "по сравнению с предыдущей версией."
        ),
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Дата публикации"),
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Опубликована"),
        help_text=_(
            "Только опубликованная версия может быть "
            "актуальной для пользователей."
        ),
    )

    class Meta:
        verbose_name = _("Версия юридического документа")
        verbose_name_plural = _("Версии юридических документов")
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "version"],
                name="unique_legal_document_version",
            ),
        ]

    def __str__(self):
        return f"{self.document.title} — {self.version}"

    def save(self, *args, **kwargs):
        """
        Гарантирует, что документ не ссылается
        на неопубликованную версию как на актуальную.
        """
        if (
            not self.is_published
            and self.document.current_version_id == self.pk
        ):
            self.document.current_version = None
            self.document.save(
                update_fields=[
                    "current_version",
                    "updated_at",
                ]
            )

        super().save(*args, **kwargs)

    def publish(self):
        """
        Публикует версию и назначает её актуальной.

        Предыдущая актуальная версия автоматически
        перестаёт быть текущей, но остаётся в истории.
        """
        self.is_published = True

        if self.published_at is None:
            self.published_at = timezone.now()

        self.save(
            update_fields=[
                "is_published",
                "published_at",
                "updated_at",
            ]
        )

        self.document.current_version = self
        self.document.save(
            update_fields=[
                "current_version",
                "updated_at",
            ]
        )

        return self

    def unpublish(self):
        """
        Снимает версию с публикации.

        Если версия была актуальной,
        связь с актуальной версией документа сбрасывается.
        """
        self.is_published = False
        self.save(
            update_fields=[
                "is_published",
                "updated_at",
            ]
        )

        if self.document.current_version_id == self.pk:
            self.document.current_version = None
            self.document.save(
                update_fields=[
                    "current_version",
                    "updated_at",
                ]
            )

        return self