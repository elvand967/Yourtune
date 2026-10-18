
# apps/notifications/admin/notification.py

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user__email", "level", "category", "is_read", "created_at")  # 5.1+
    list_filter = ("level", "category", "is_read", "created_at")
    show_facets = admin.ShowFacets.ALWAYS                    # 5.0+: счётчики в фильтрах
    search_fields = ("title", "message", "user__email")
    raw_id_fields = ("user",)
    list_select_related = ("user",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "read_at")
    actions = ("mark_read", "mark_unread")

    @admin.action(description=_("Отметить прочитанными"))
    def mark_read(self, request, queryset):
        queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())

    @admin.action(description=_("Отметить непрочитанными"))
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)