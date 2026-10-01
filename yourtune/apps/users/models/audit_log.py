# apps/users/models/audit_log.py
# =====================================

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.core.models import UUIDModel


class AuditLog(UUIDModel):
    """
    Лог действий пользователей (аудит).
    """
    class Action(models.TextChoices):
        LOGIN = 'login', _('Вход')
        LOGOUT = 'logout', _('Выход')
        PASSWORD_CHANGE = 'password_change', _('Смена пароля')
        PROFILE_UPDATE = 'profile_update', _('Обновление профиля')
        SETTINGS_CHANGE = 'settings_change', _('Изменение настроек')
        ROLE_ASSIGNED = 'role_assigned', _('Назначение роли')
        ROLE_REMOVED = 'role_removed', _('Удаление роли')
        USER_CREATED = 'user_created', _('Создание пользователя')
        USER_DEACTIVATED = 'user_deactivated', _('Деактивация пользователя')
        USER_ACTIVATED = 'user_activated', _('Активация пользователя')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name=_("Пользователь"),
        db_index=True,
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        verbose_name=_("Действие"),
        db_index=True,
    )
    details = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Детали"),
        help_text=_("JSON или текст с деталями действия")
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP-адрес"),
    )
    user_agent = models.TextField(
        blank=True,
        default='',
        verbose_name=_("User Agent"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Время"),
        db_index=True,
    )

    class Meta:
        verbose_name = _("Лог аудита")
        verbose_name_plural = _("Логи аудита")
        db_table = 'users_auditlog'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.email} — {self.get_action_display()} ({self.created_at})'