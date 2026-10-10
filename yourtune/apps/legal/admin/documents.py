# apps/legal/admin/documents.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.legal.models import LegalDocument, LegalDocumentVersion


class LegalDocumentVersionInline(admin.TabularInline):
    """
    Версии документа внутри карточки юридического документа.
    """

    model = LegalDocumentVersion
    extra = 0
    fields = (
        "version",
        "title",
        "is_published",
        "published_at",
        "summary",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    show_change_link = True


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """
    Управление юридическими документами.
    """

    list_display = (
        "title",
        "document_type",
        "slug",
        "current_version",
        "is_required",
        "is_active",
        "updated_at",
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

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (LegalDocumentVersionInline,)

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "document_type",
                    "title",
                    "slug",
                    "description",
                )
            },
        ),
        (
            _("Статус"),
            {
                "fields": (
                    "is_active",
                    "is_required",
                    "current_version",
                )
            },
        ),
        (
            _("Служебное"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.action(description=_("Сделать выбранные документы активными"))
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_("Сделать выбранные документы неактивными"))
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    actions = (
        "make_active",
        "make_inactive",
    )


@admin.register(LegalDocumentVersion)
class LegalDocumentVersionAdmin(admin.ModelAdmin):
    """
    Управление конкретными редакциями документов.
    """

    list_display = (
        "document",
        "version",
        "title",
        "is_published",
        "published_at",
        "created_at",
    )

    list_filter = (
        "document",
        "is_published",
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
            _("Документ и версия"),
            {
                "fields": (
                    "document",
                    "version",
                    "title",
                )
            },
        ),
        (
            _("Содержание"),
            {
                "fields": (
                    "content",
                    "summary",
                )
            },
        ),
        (
            _("Публикация"),
            {
                "fields": (
                    "is_published",
                    "published_at",
                )
            },
        ),
        (
            _("Служебное"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.action(description=_("Опубликовать выбранные версии"))
    def publish_versions(self, request, queryset):
        for version in queryset:
            version.publish()

    actions = (
        "publish_versions",
    )