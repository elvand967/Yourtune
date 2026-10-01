# apps/users/models/playlist.py
"""
Заглушка для модели Playlist.
TODO: Реализовать полноценную модель с связью ManyToMany к аффирмациям/практикам.
"""

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel


class Playlist(UUIDModel):
    """
    Плейлист пользователя — коллекция аффирмаций/практик.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name=_('Пользователь')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name=_('URL')
    )
    description = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Описание')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Публичный')
    )

    class Meta:
        verbose_name = _('Плейлист')
        verbose_name_plural = _('Плейлисты')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Playlist.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)