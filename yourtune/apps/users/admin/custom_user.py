
# apps/users/admin/custom_user.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.forms.custom_user import CustomUserCreationForm, CustomUserChangeForm
from apps.users.models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = "user"
    extra = 0
    max_num = 1


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    inlines = (ProfileInline,)

    list_display = ("email", "first_name", "middle_name", "last_name", "is_staff", "is_active", "is_verified")
    list_filter = ("is_staff", "is_active", "is_superuser", "is_verified")
    search_fields = ("email", "first_name", "middle_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "middle_name", "last_name")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_verified",
                ),
            },
        ),
    )