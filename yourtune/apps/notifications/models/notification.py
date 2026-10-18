
# apps/notifications/models/notification.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.abstract import UUIDModel
from apps.notifications.categories import Category


class NotificationQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def unread(self):
        return self.filter(is_read=False)

    def mark_read(self):
        """Массово отмечает уведомления прочитанными одним UPDATE-запросом."""
        now = timezone.now()
        return self.filter(is_read=False).update(
            is_read=True,
            read_at=now,
        )


class Notification(UUIDModel):
    class Level(models.TextChoices):
        SUCCESS = "success", _("Успешно")
        INFO = "info", _("Информация")
        WARNING = "warning", _("Предупреждение")
        ERROR = "error", _("Ошибка")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Получатель"),
    )
    level = models.CharField(
        _("Уровень"),
        max_length=10,
        choices=Level.choices,
        default=Level.INFO,
    )
    category = models.CharField(
        _("Категория"),
        max_length=50,
        choices=Category.choices,
        default=Category.SYSTEM,
        db_index=True,
    )
    title = models.CharField(_("Заголовок"), max_length=255)
    message = models.TextField(_("Текст"), blank=True)
    url = models.CharField(
        _("Ссылка на действие"),
        max_length=500,
        blank=True,
        help_text=_("Внутренний путь, например /account/settings/"),
    )
    is_read = models.BooleanField(_("Прочитано"), default=False)
    read_at = models.DateTimeField(_("Прочитано в"), null=True, blank=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_read", "-created_at"],
                name="notif_user_read_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(is_read=False) | Q(read_at__isnull=False),
                name="notif_read_has_read_at",
            ),
        ]

    def __str__(self):
        return f"[{self.level.upper()}] {self.user} — {self.title}"

    def _sync_read_at(self):
        if self.is_read and self.read_at is None:
            self.read_at = timezone.now()
        elif not self.is_read:
            self.read_at = None

    def clean(self):
        super().clean()

        if self.is_read and self.read_at is None:
            raise ValidationError(
                _("Для прочитанного уведомления необходимо указать дату прочтения.")
            )

        if not self.is_read and self.read_at is not None:
            raise ValidationError(
                _("Непрочитанное уведомление не может иметь дату прочтения.")
            )

    def save(self, *args, **kwargs):
        self._sync_read_at()
        super().save(*args, **kwargs)

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])