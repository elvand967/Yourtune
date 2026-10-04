# apps/users/forms/auth.py
# ========================
# Кастомные формы аутентификации для django-allauth.
#
# ВАЖНО: get_user_model() вызывается ВНУТРИ методов,
# а не на уровне модуля. Это предотвращает ошибку
# AppRegistryNotReady при импорте форм через urls -> views -> forms.

from django import forms
from allauth.account.forms import (
    SignupForm,
    LoginForm,
    ResetPasswordForm,
)
from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class CustomSignupForm(SignupForm):
    """Форма регистрации по email + пароль."""

    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form__control',
            'placeholder': 'Имя',
        }),
        label='Имя',
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form__control',
            'placeholder': 'Фамилия',
        }),
        label='Фамилия',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Email',
            'type': 'email',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Подтверждение пароля',
        })

    def save(self, request):
        """Сохраняем пользователя с именем и фамилией."""
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()
        return user


class CustomLoginForm(LoginForm):
    """
    Форма входа по email + пароль.

    Особенность: если пользователь зарегистрирован только через
    соц. сеть (Google/Yandex) и не имеет пароля —
    НЕ показываем ошибку на форме, а передаём view флаг
    social_redirect_email. View перенаправит на единую
    страницу входа с понятным сообщением и кнопками
    Google/Yandex.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Email соц.-пользователя (заполняется в clean())
        # View прочитает его для персонального сообщения
        self.social_redirect_email = None

        self.fields['login'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Email',
            'type': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Пароль',
        })

    def clean(self):
        """
        Порядок проверки:
        1. Получаем email из формы.
        2. Если пользователь существует, но без пароля и с соц. аккаунтом —
           запоминаем email и добавляем служебную ошибку
           (чтобы форма не прошла валидацию и не попыталась войти).
        3. Иначе — стандартная проверка учётных данных allauth.
        """
        # Ленивый импорт: приложения уже загружены при обработке запроса
        from django.contrib.auth import get_user_model
        User = get_user_model()

        login = self.cleaned_data.get('login')

        if login:
            try:
                user = User.objects.get(email__iexact=login)

                # Соц.-пользователь без пароля
                if (
                    not user.has_usable_password()
                    and user.socialaccount_set.exists()
                ):
                    # Сохраняем email для view —
                    # он покажет персональное сообщение на unified-странице
                    self.social_redirect_email = user.email

                    # Служебная ошибка: блокирует вход,
                    # но её текст пользователь НЕ увидит —
                    # view перехватит и сделает redirect
                    self.add_error(
                        None,
                        'SOCIAL_ONLY_ACCOUNT',  # служебный маркер
                    )
                    return self.cleaned_data

            except User.DoesNotExist:
                # Email не найден — стандартная проверка allauth
                pass

        # Обычная проверка учётных данных
        return super().clean()


class CustomSocialSignupForm(SocialSignupForm):
    """Форма завершения регистрации через соц. сеть."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form__control',
            'type': 'email',
            'readonly': True,
        }),
        label='Email',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = (
            self.sociallogin.email_addresses[0].email
            if self.sociallogin.email_addresses
            else ''
        )


class CustomResetPasswordForm(ResetPasswordForm):
    """
    Форма восстановления пароля.

    Разрешает сброс пароля соц.-пользователям
    (у которых unusable password).
    """

    def get_users(self, email):
        """
        Возвращает пользователей для отправки письма.

        Включаем:
        - обычных пользователей (есть пароль);
        - соц.-пользователей (нет пароля, но есть соц. аккаунт).
        """
        # ✅ get_user_model() ВНУТРИ метода — безопасно
        from django.contrib.auth import get_user_model
        User = get_user_model()

        active_users = User.objects.filter(
            email__iexact=email,
            is_active=True,
        )

        return (
            u for u in active_users
            if u.has_usable_password() or self._has_social_account(u)
        )

    def _has_social_account(self, user):
        """Проверяет наличие соц. аккаунта у пользователя."""
        return user.socialaccount_set.exists()