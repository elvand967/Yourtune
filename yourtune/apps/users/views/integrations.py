# apps/users/views/integrations.py
# =====================================

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class IntegrationsView(LoginRequiredMixin, TemplateView):
    """Главная страница интеграций."""
    template_name = 'users/integrations/index.html'


class ApiTokensView(LoginRequiredMixin, TemplateView):
    """Управление API токенами."""
    template_name = 'users/integrations/api_tokens.html'


class SocialAccountsView(LoginRequiredMixin, TemplateView):
    """Управление социальными аккаунтами."""
    template_name = 'users/integrations/social_accounts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_accounts'] = self.request.user.social_accounts.all()
        return context