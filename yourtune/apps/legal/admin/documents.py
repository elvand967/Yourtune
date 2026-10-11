# apps/legal/admin/documents.py
# ===============================

from django.contrib import admin

from apps.legal.models import LegalDocument, LegalDocumentVersion


class LegalDocumentVersionInline(admin.TabularInline):
    """
    Версии документа на странице юридического документа.
    """

    model = LegalDocumentVersion
    extra = 0
    fields = (
        "version",
        "title",
        "is_published",
        "published_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    show_change_link = True


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """
    Админка юридических документов.
    """

    list_display = (
        "title",
        "document_type",
        "slug",
        "is_active",
        "is_required",
        "current_version",
    )

    list_filter = (
        "document_type",
        "is_active",
        "is_required",
    )

    search_fields = (
        "title",
        "slug",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    inlines = [
        LegalDocumentVersionInline,
    ]

    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "title",
                    "slug",
                    "document_type",
                    "description",
                )
            },
        ),
        (
            "Статус",
            {
                "fields": (
                    "is_active",
                    "is_required",
                    "current_version",
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


@admin.register(LegalDocumentVersion)
class LegalDocumentVersionAdmin(admin.ModelAdmin):
    """
    Админка версий юридических документов.
    """

    list_display = (
        "document",
        "version",
        "title",
        "is_published",
        "published_at",
    )

    list_filter = (
        "is_published",
        "document",
    )

    search_fields = (
        "document__title",
        "version",
        "title",
        "summary",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Версия",
            {
                "fields": (
                    "document",
                    "version",
                    "title",
                )
            },
        ),
        (
            "Содержание",
            {
                "fields": (
                    "content",
                    "summary",
                )
            },
        ),
        (
            "Публикация",
            {
                "fields": (
                    "is_published",
                    "published_at",
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