# apps/users/views/auth.py

from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import redirect
from allauth.account.views import LoginView, SignupView, LogoutView
from allauth.socialaccount.views import SignupView as SocialSignupView
from apps.users.forms.auth import CustomSignupForm, CustomLoginForm, CustomSocialSignupForm


class UnifiedLoginView(TemplateView):
    """Единая страница входа с Email и социальными провайдерами."""
    template_name = 'users/auth/unified_login.html'


class CustomSignupView(SignupView):
    """Переопределение view регистрации."""
    form_class = CustomSignupForm
    template_name = 'users/auth/signup.html'
    success_url = reverse_lazy('users:profile_detail')


class CustomLoginView(LoginView):
    """Страница входа через Email."""
    form_class = CustomLoginForm
    template_name = 'users/auth/email_login.html'

    def get_success_url(self):
        return reverse_lazy('users:profile_detail')


class CustomLogoutView(LogoutView):
    """Переопределение view выхода."""
    def get_success_url(self):
        return reverse_lazy('main:home')


class CustomSocialSignupView(SocialSignupView):
    """Переопределение view регистрации через соц. сеть."""
    form_class = CustomSocialSignupForm
    template_name = 'users/auth/social_signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('users:profile_detail')