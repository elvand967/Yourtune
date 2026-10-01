# apps/users/views/security.py
# =====================================

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages


class PasswordChangeView(LoginRequiredMixin, DjangoPasswordChangeView):
    """Смена пароля пользователя."""
    template_name = 'users/security/password_change.html'
    success_url = reverse_lazy('users:profile_detail')

    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменён.')
        return super().form_valid(form)


class SessionsView(LoginRequiredMixin, TemplateView):
    """Активные сессии пользователя."""
    template_name = 'users/security/sessions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: реализовать получение сессий из БД/кэша
        context['sessions'] = []
        return context


class TwoFactorView(LoginRequiredMixin, TemplateView):
    """Настройки двухфакторной аутентификации."""
    template_name = 'users/security/two_factor.html'