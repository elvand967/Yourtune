# apps/legal/admin/consents.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.legal.models import UserLegalConsent


@admin.register(UserLegalConsent)
class UserLegalConsentAdmin(admin.ModelAdmin):
    """
    Просмотр и управление фактами принятия
    юридических документов пользователями.
    """

    list_display = (
        "user",
        "document_title",
        "document_version",
        "source",
        "accepted_at",
        "ip_address",
    )

    list_filter = (
        "source",
        "document_version__document",
        "accepted_at",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "document_version__title",
        "document_version__version",
    )

    autocomplete_fields = (
        "user",
        "document_version",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            _("Согласие"),
            {
                "fields": (
                    "user",
                    "document_version",
                    "source",
                    "accepted_at",
                )
            },
        ),
        (
            _("Технические данные"),
            {
                "fields": (
                    "ip_address",
                    "user_agent",
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

    @admin.display(description=_("Документ"))
    def document_title(self, obj):
        return obj.document_version.document.title