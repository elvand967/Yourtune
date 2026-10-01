# apps/users/models/role.py
# =====================================

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.core.models import UUIDModel


class Role(UUIDModel):
    """
    Кастомные роли для управления доступом пользователей.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Название"),
        help_text=_("Уникальное имя роли, например: Moderator, Editor, VIP")
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        verbose_name=_("Слаг"),
        help_text=_("URL-безопасное имя роли")
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Описание")
    )
    permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        verbose_name=_("Разрешения"),
        help_text=_("Разрешения Django, привязанные к роли")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активна"),
        help_text=_("Если неактивна, роль не применяется к пользователям")
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Создана")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Обновлена")
    )

    class Meta:
        verbose_name = _("Роль")
        verbose_name_plural = _("Роли")
        db_table = 'users_role'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class UserRole(UUIDModel):
    """
    Связь пользователь ↔ роль.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_("Пользователь"),
        db_index=True,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_("Роль"),
        db_index=True,
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Назначена")
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name=_("Назначил"),
    )
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Заметки"),
        help_text=_("Комментарий к назначению роли")
    )

    class Meta:
        verbose_name = _("Роль пользователя")
        verbose_name_plural = _("Роли пользователей")
        db_table = 'users_userrole'
        unique_together = ('user', 'role')
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['user', '-assigned_at']),
        ]

    def __str__(self):
        return f'{self.user.email} → {self.role.name}'