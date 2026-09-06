
# apps/core/models/abstract.py

import uuid
from django.db import models
from apps.core.utils.slugify_seo import slugify_seo


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        abstract = True
        verbose_name = "Модель с UUID"
        verbose_name_plural = "Модели с UUID"


'''Абстрактная модель с UUID,
полями title и глобальной автогенерацией SEO-эффективного slug (без стоп-слов ("и"; "в"; "для" и т.п.)).
Поле slug - уникально в пределах модели'''
class NamedSlugModel(UUIDModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, blank=True, unique=True,
        help_text="SEO‑дружественный URL; если пусто — генерируется автоматически из title."
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify_seo(self.title)
            self.slug = self.make_unique_slug(base_slug)
        super().save(*args, **kwargs)

    def make_unique_slug(self, base_slug):
        """
        Обеспечивает уникальность slug для конкретной модели.
        """
        model_class = self.__class__
        slug = base_slug
        counter = 1

        while model_class.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug
