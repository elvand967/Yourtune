# apps/users/views/admin/audit.py
# =====================================

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView

from apps.users.models import AuditLog


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AdminAuditLogView(StaffRequiredMixin, ListView):
    """Лог аудита (админ-панель)."""
    model = AuditLog
    template_name = 'users/admin/audit/list.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        return AuditLog.objects.select_related('user').order_by('-created_at')


class AdminAuditLogDetailView(StaffRequiredMixin, DetailView):
    """Детали записи аудита (админ-панель)."""
    model = AuditLog
    template_name = 'users/admin/audit/detail.html'
    context_object_name = 'log'