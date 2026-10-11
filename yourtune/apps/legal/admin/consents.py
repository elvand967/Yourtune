# apps/legal/admin/consents.py
# ==============================

from django.contrib import admin

from apps.legal.models import UserLegalConsent


@admin.register(UserLegalConsent)
class UserLegalConsentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "document_version",
        "source",
        "accepted_at",
    )

    list_filter = (
        "source",
        "accepted_at",
    )

    search_fields = (
        "user__email",
        "document_version__title",
    )

    readonly_fields = (
        "user",
        "document_version",
        "source",
        "ip_address",
        "user_agent",
        "accepted_at",
    )