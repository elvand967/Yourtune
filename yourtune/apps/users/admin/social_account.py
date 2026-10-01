
# apps/users/admin/social_account.py

from django.contrib import admin

from apps.users.forms.social_account import SocialAccountForm
from apps.users.models import SocialAccount


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    form = SocialAccountForm
    list_display = ("user", "provider", "provider_uid", "is_primary", "updated_at")
    list_filter = ("provider", "is_primary", "created_at")
    search_fields = ("user__email", "provider_uid", "email")
    ordering = ("provider", "user__email")
    readonly_fields = ("created_at", "updated_at")