# apps/users/views/admin/roles.py
# =====================================

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from apps.users.models import Role


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AdminRoleListView(StaffRequiredMixin, ListView):
    """Список ролей (админ-панель)."""
    model = Role
    template_name = 'users/admin/roles/list.html'
    context_object_name = 'roles'
    paginate_by = 20

    def get_queryset(self):
        return Role.objects.prefetch_related('permissions').order_by('name')


class AdminRoleCreateView(StaffRequiredMixin, CreateView):
    """Создание роли (админ-панель)."""
    model = Role
    template_name = 'users/admin/roles/form.html'
    fields = ['name', 'slug', 'description', 'permissions', 'is_active']
    success_url = reverse_lazy('users:admin_role_list')

    def form_valid(self, form):
        messages.success(self.request, f'Роль "{form.instance.name}" создана.')
        return super().form_valid(form)


class AdminRoleUpdateView(StaffRequiredMixin, UpdateView):
    """Редактирование роли (админ-панель)."""
    model = Role
    template_name = 'users/admin/roles/form.html'
    fields = ['name', 'slug', 'description', 'permissions', 'is_active']
    success_url = reverse_lazy('users:admin_role_list')

    def form_valid(self, form):
        messages.success(self.request, f'Роль "{form.instance.name}" обновлена.')
        return super().form_valid(form)


class AdminRoleDeleteView(StaffRequiredMixin, DeleteView):
    """Удаление роли (админ-панель)."""
    model = Role
    template_name = 'users/admin/roles/confirm_delete.html'
    success_url = reverse_lazy('users:admin_role_list')

    def delete(self, request, *args, **kwargs):
        role_name = self.get_object().name
        messages.success(request, f'Роль "{role_name}" удалена.')
        return super().delete(request, *args, **kwargs)