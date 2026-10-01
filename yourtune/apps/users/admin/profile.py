
# apps/users/admin/profile.py

from django.contrib import admin

from apps.users.forms.profile import ProfileForm
from apps.users.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileForm
    list_display = ("user", "gender", "date_of_birth", "voice_preference", "location", "is_public", "updated_at")
    list_filter = ("gender", "voice_preference", "is_public", "language", "timezone")
    search_fields = ("user__email", "user__first_name", "user__last_name", "bio", "location")
    ordering = ("user__email",)
    readonly_fields = ("created_at", "updated_at")