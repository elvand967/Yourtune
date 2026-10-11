# apps/core/admin/seo.py
# ========================

from django.contrib import admin

from apps.core.models.seo import SEOReplacement, StopWord


@admin.register(StopWord)
class StopWordAdmin(admin.ModelAdmin):
    """
    Админка SEO-стоп-слов.

    Используется генератором slugify_seo()
    для удаления незначимых слов из slug.
    """

    list_display = (
        "lang",
        "word",
    )

    list_filter = (
        "lang",
    )

    search_fields = (
        "word",
    )

    ordering = (
        "lang",
        "word",
    )

    fieldsets = (
        (
            "Стоп-слово",
            {
                "fields": (
                    "lang",
                    "word",
                )
            },
        ),
        (
            "Служебное",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(SEOReplacement)
class SEOReplacementAdmin(admin.ModelAdmin):
    """
    Админка SEO-замен.

    Пример:
    айфон → iphone
    """

    list_display = (
        "source_word",
        "replacement",
    )

    search_fields = (
        "source_word",
        "replacement",
    )

    ordering = (
        "source_word",
    )

    fieldsets = (
        (
            "SEO-замена",
            {
                "fields": (
                    "source_word",
                    "replacement",
                )
            },
        ),
        (
            "Служебное",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )