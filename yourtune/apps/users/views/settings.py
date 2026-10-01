# apps/users/views/settings.py
# =====================================

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from apps.users.models import Profile


class SettingsView(LoginRequiredMixin, TemplateView):
    """Главная страница настроек."""
    template_name = 'users/settings/index.html'


class AccountSettingsView(LoginRequiredMixin, UpdateView):
    """Настройки аккаунта (язык, часовой пояс, тема)."""
    model = Profile
    template_name = 'users/settings/account.html'
    fields = ['language', 'timezone']
    success_url = reverse_lazy('users:settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Настройки аккаунта сохранены.')
        return super().form_valid(form)


class PrivacySettingsView(LoginRequiredMixin, UpdateView):
    """Настройки приватности."""
    model = Profile
    template_name = 'users/settings/privacy.html'
    fields = ['is_public', 'privacy_level']
    success_url = reverse_lazy('users:settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Настройки приватности сохранены.')
        return super().form_valid(form)


class NotificationsView(LoginRequiredMixin, TemplateView):
    """Настройки уведомлений."""
    template_name = 'users/settings/notifications.html'