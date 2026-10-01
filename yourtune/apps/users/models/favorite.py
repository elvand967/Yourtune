# apps/users/models/favorite.py
"""
Заглушка для модели Favorite.
TODO: Реализовать полноценную модель с GenericForeignKey.
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel


class Favorite(UUIDModel):
    """
    Избранные элементы пользователя (аффирмации, практики, статьи).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь')
    )

    # Generic relation для любых объектов
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип контента')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        ordering = ['-created_at']
        unique_together = ['user', 'content_type', 'object_id']

    def __str__(self):
        return f'{self.user.email} — {self.content_type}'