# apps/legal/models/documents.py
# ================================

import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import UUIDModel
from apps.core.utils.slugify_seo import slugify_seo


class LegalDocument(UUIDModel):
    """
    Юридический документ проекта YourTune.

    Документ может быть:
    - публичной политикой;
    - условиями использования сервиса;
    - согласием пользователя;
    - правилами публикации контента;
    - документом для платных функций и подписок.
    """

    class DocumentType(models.TextChoices):
        # ==================================================
        # Базовые документы
        # ==================================================
        PRIVACY_POLICY = "privacy_policy", _("Политика конфиденциальности")
        TERMS_OF_USE = "terms_of_use", _("Правила использования сервиса")

        PERSONAL_DATA_CONSENT = (
            "personal_data_consent",
            _("Согласие на обработку персональных данных"),
        )

        EMAIL_NOTIFICATIONS_CONSENT = (
            "email_notifications_consent",
            _("Согласие на получение email-уведомлений"),
        )

        COOKIE_POLICY = "cookie_policy", _("Политика cookie")

        USER_CONTENT_RULES = (
            "user_content_rules",
            _("Правила публикации пользовательского контента"),
        )

        MODERATION_POLICY = (
            "moderation_policy",
            _("Политика модерации и жалоб"),
        )

        DMCA_POLICY = (
            "dmca_policy",
            _("Уведомление об авторских правах / DMCA"),
        )

        # ==================================================
        # Платные услуги и подписки
        # ==================================================
        PAID_SERVICES_TERMS = (
            "paid_services_terms",
            _("Условия оказания платных услуг / оферта"),
        )

        REFUND_POLICY = "refund_policy", _("Политика возвратов")

        PAYMENT_DATA_POLICY = (
            "payment_data_policy",
            _("Политика обработки платежных данных"),
        )

        RECURRING_PAYMENT_CONSENT = (
            "recurring_payment_consent",
            _("Согласие на списание регулярных платежей"),
        )

        PRICING_POLICY = (
            "pricing_policy",
            _("Политика цен и изменения тарифов"),
        )

        # ==================================================
        # API, мобильное приложение и данные
        # ==================================================
        API_TERMS = "api_terms", _("Условия использования API")

        MOBILE_PRIVACY_POLICY = (
            "mobile_privacy_policy",
            _("Политика конфиденциальности для мобильного приложения"),
        )

        THIRD_PARTY_LIST = (
            "third_party_list",
            _("Список третьих лиц"),
        )

        CROSS_BORDER_TRANSFER_POLICY = (
            "cross_border_transfer_policy",
            _("Порядок трансграничной передачи данных"),
        )

    document_type = models.CharField(
        max_length=64,
        choices=DocumentType.choices,
        verbose_name=_("Тип документа"),
        help_text=_(
            "Категория юридического документа. "
            "Тип не уникален: в будущем могут быть созданы "
            "дополнительные документы одной категории."
        ),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Название документа"),
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name=_("SEO slug"),
        help_text=_(
            "Используется в публичных ссылках. "
            "Если оставить пустым, будет сформирован автоматически "
            "из названия документа."
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

    menu_title = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Краткое название в меню"),
        help_text=_(
            "Отображается в навигации сайта. "
            "Если не заполнено, используется название документа."
        ),
    )

    menu_order = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Порядок в меню"),
        help_text=_(
            "Чем меньше значение, тем выше документ "
            "отображается в меню."
        ),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен"),
        help_text=_(
            "Активный документ отображается в публичном меню "
            "и может требоваться для принятия пользователями."
        ),
    )

    is_required = models.BooleanField(
        default=True,
        verbose_name=_("Обязателен для принятия"),
        help_text=_(
            "Обязательный документ блокирует доступ к защищённым разделам "
            "до принятия его актуальной версии. "
            "Для информационных документов обычно установите значение «Нет»."
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
        ordering = ["menu_order", "title"]
        indexes = [
            models.Index(
                fields=["document_type", "is_active"],
                name="legal_document_type_active_idx",
            ),
            models.Index(
                fields=["is_active", "menu_order"],
                name="legal_document_menu_idx",
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Возвращает публичный URL актуальной страницы документа.
        """
        return reverse(
            "legal:document_detail",
            kwargs={"slug": self.slug},
        )

    @property
    def menu_label(self):
        """
        Возвращает краткое название для навигации.
        """
        return self.menu_title or self.title

    def get_current_version(self):
        """
        Возвращает актуальную версию документа.
        """
        return self.current_version

    def _generate_base_slug(self):
        """
        Формирует базовый SEO slug из названия документа.

        Использует стоп-слова, SEO-замены и транслитерацию
        из apps/core/utils/slugify_seo.py.
        """
        base_slug = slugify_seo(
            self.title,
            stop_langs=("ru", "en"),
            max_length=255,
            allow_unicode=False,
        )

        if base_slug:
            return base_slug

        # Защита от пустого названия или полного удаления
        # всех слов стоп-словарём.
        fallback_source = str(self.pk or uuid.uuid4())

        return slugify_seo(
            fallback_source,
            stop_langs=(),
            max_length=255,
            allow_unicode=False,
        )

    def _generate_unique_slug(self):
        """
        Генерирует уникальный slug для документа.

        Если базовый slug уже занят, добавляет числовой суффикс:
        -2, -3, -4 и так далее.
        """
        base_slug = self._generate_base_slug()

        slug = base_slug

        queryset = LegalDocument.objects.all()

        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        counter = 2

        while queryset.filter(slug=slug).exists():
            suffix = f"-{counter}"
            max_base_length = 255 - len(suffix)

            slug = f"{base_slug[:max_base_length]}{suffix}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        """
        Создаёт SEO slug при первом сохранении документа.

        Если slug уже указан вручную, он не перезаписывается:
        это защищает существующие публичные ссылки.
        """
        if not self.slug:
            self.slug = self._generate_unique_slug()

            update_fields = kwargs.get("update_fields")

            if update_fields is not None:
                update_fields = set(update_fields)
                update_fields.add("slug")
                kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)


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