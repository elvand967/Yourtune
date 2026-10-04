# apps/users/views/auth.py
# ========================
# Кастомные views аутентификации для django-allauth.
#
# Модуль содержит:
# - UnifiedLoginView       — единая страница входа (соц. сети + email)
# - CustomLoginView        — вход по email + пароль
# - CustomSignupView       — регистрация по email + пароль
# - CustomLogoutView       — выход
# - CustomSocialSignupView — завершение регистрации через соц. сеть
#
# Важно: allauth сам обрабатывает OAuth2-flow для Google/Yandex.
# Наши views нужны только для кастомных шаблонов и форм.

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import redirect
from allauth.account.views import LoginView, SignupView, LogoutView
from allauth.socialaccount.views import SignupView as SocialSignupView
from apps.users.forms.auth import (
    CustomSignupForm,
    CustomLoginForm,
    CustomSocialSignupForm,
)


class UnifiedLoginView(TemplateView):
    """
    Единая страница входа.

    Показывает:
    - кнопки входа через Google / Yandex;
    - кнопку перехода к входу по email + пароль;
    - ссылки на регистрацию и восстановление пароля.
    """
    template_name = 'users/auth/unified_login.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Если пользователь уже авторизован —
        отправляем его в профиль, чтобы не показывать форму входа.
        """
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """
    Страница входа через email + пароль.

    Особенность: если пользователь зарегистрирован только через
    соц. сеть (Google/Yandex), форма выставляет
    social_redirect_email. В этом случае мы:
    1. Не показываем ошибку на форме.
    2. Добавляем info-сообщение с email.
    3. Перенаправляем на единую страницу входа,
       где есть кнопки Google/Yandex и ссылка «Установить пароль?».
    """
    form_class = CustomLoginForm
    template_name = 'users/auth/email_login.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Авторизованного пользователя не пускаем на страницу входа.
        """
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Куда перенаправлять после успешного входа."""
        return reverse_lazy('users:profile_detail')

    def form_invalid(self, form):
        """
        Вызывается, когда форма не прошла валидацию.

        Если форма пометила соц.-пользователя
        (social_redirect_email) — перенаправляем на единую
        страницу входа с info-сообщением.
        """
        social_email = getattr(form, 'social_redirect_email', None)

        if social_email:
            # Персональное сообщение для unified-страницы
            messages.info(
                self.request,
                f'{social_email} — аккаунт был создан через '
                f'Google/Yandex. Войдите через социальную сеть '
                f'или установите пароль по email.'
            )

            # Редирект на единую страницу входа
            return redirect('users:login')

        # Обычная обработка: показать форму с ошибками
        return super().form_invalid(form)


class CustomSignupView(SignupView):
    """
    Страница регистрации по email + пароль.

    Использует CustomSignupForm с полями
    first_name и last_name.
    """
    form_class = CustomSignupForm
    template_name = 'users/auth/signup.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Авторизованного пользователя не пускаем на регистрацию.
        """
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Куда перенаправлять после успешной регистрации."""
        return reverse_lazy('users:profile_detail')


class CustomLogoutView(LogoutView):
    """
    Выход из аккаунта.

    ACCOUNT_LOGOUT_ON_GET = True в настройках позволяет
    выходить по GET-запросу (простая ссылка в меню).
    """

    def get_success_url(self):
        """Куда перенаправлять после выхода."""
        return reverse_lazy('main:home')


class CustomSocialSignupView(SocialSignupView):
    """
    Завершение регистрации через соц. сеть.

    Показывается редко — только если allauth не смог
    автоматически создать пользователя
    (например, провайдер не передал email).
    """
    form_class = CustomSocialSignupForm
    template_name = 'users/auth/social_signup.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Авторизованного пользователя не пускаем.
        """
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Куда перенаправлять после завершения регистрации."""
        return reverse_lazy('users:profile_detail')