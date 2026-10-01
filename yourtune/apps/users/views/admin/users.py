# apps/users/views/admin/users.py
# =====================================

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

User = get_user_model()


class StaffRequiredMixin(UserPassesTestMixin):
    """Миксин для ограничения доступа стаффу/суперюзерам."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AdminUserListView(StaffRequiredMixin, ListView):
    """Список всех пользователей (админ-панель)."""
    model = User
    template_name = 'users/admin/users/list.html'
    context_object_name = 'users'
    paginate_by = 20


class AdminUserDetailView(StaffRequiredMixin, DetailView):
    """Детали пользователя (админ-панель)."""
    model = User
    template_name = 'users/admin/users/detail.html'
    context_object_name = 'user'


class AdminUserUpdateView(StaffRequiredMixin, UpdateView):
    """Редактирование пользователя (админ-панель)."""
    model = User
    template_name = 'users/admin/users/edit.html'
    fields = ['first_name', 'middle_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_verified']
    success_url = reverse_lazy('users:admin_user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Пользователь обновлён.')
        return super().form_valid(form)