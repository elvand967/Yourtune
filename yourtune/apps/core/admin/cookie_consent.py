
# apps/core/admin/cookie_consent.py

from django.contrib import admin

from apps.core.models import CookieConsent


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "necessary",
        "analytics",
        "marketing",
        "policy_version",
        "source",
        "created_at",
    )

    list_filter = (
        "analytics",
        "marketing",
        "policy_version",
        "source",
        "created_at",
    )

    search_fields = (
        "user__email",
        "session_key",
    )

    readonly_fields = (
        "user",
        "session_key",
        "necessary",
        "analytics",
        "marketing",
        "policy_version",
        "source",
        "ip_address",
        "user_agent",
        "created_at",
    )