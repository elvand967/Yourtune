# apps/users/forms/auth.py
# ========================
# Кастомные формы аутентификации для django-allauth.
#
# ВАЖНО: get_user_model() вызывается ВНУТРИ методов,
# а не на уровне модуля. Это предотвращает ошибку
# AppRegistryNotReady при импорте форм через urls -> views -> forms.

from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import (
    SignupForm,
    LoginForm,
    ResetPasswordForm,
)
from allauth.socialaccount.forms import SignupForm as SocialSignupForm

from apps.legal.models import LegalDocument, UserLegalConsent
from apps.legal.services import LegalDocumentService


class ConsentMixin:
    """
    Общая логика обязательного принятия
    юридических документов.
    """

    consent_source = UserLegalConsent.ConsentSource.SIGNUP

    def add_consent_fields(self):
        """
        Добавляет два обязательных чекбокса согласия.
        """
        self.fields["accept_privacy_policy"] = forms.BooleanField(
            required=True,
            label=_("Я прочитал(а) и принимаю Политику конфиденциальности"),
        )

        self.fields["accept_terms_of_use"] = forms.BooleanField(
            required=True,
            label=_("Я прочитал(а) и принимаю Правила использования сервиса"),
        )

    def clean_consents(self):
        """
        Проверяет явное согласие с обоими документами.
        """
        if not self.cleaned_data.get("accept_privacy_policy"):
            self.add_error(
                "accept_privacy_policy",
                _(
                    "Для регистрации необходимо принять "
                    "Политику конфиденциальности."
                ),
            )

        if not self.cleaned_data.get("accept_terms_of_use"):
            self.add_error(
                "accept_terms_of_use",
                _(
                    "Для регистрации необходимо принять "
                    "Правила использования сервиса."
                ),
            )

        return self.cleaned_data

    def save_consents(self, request, user):
        """
        Фиксирует согласия пользователя
        на актуальные версии документов.
        """
        LegalDocumentService.accept_documents_by_types(
            user=user,
            request=request,
            document_types=[
                LegalDocument.DocumentType.PRIVACY_POLICY,
                LegalDocument.DocumentType.TERMS_OF_USE,
            ],
            source=self.consent_source,
        )


class CustomSignupForm(ConsentMixin, SignupForm):
    """
    Форма регистрации по email + пароль.
    """

    consent_source = UserLegalConsent.ConsentSource.SIGNUP

    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": "Имя",
            }
        ),
        label=_("Имя"),
    )

    accept_privacy_policy = forms.BooleanField(
        required=True,
        label=_("Я прочитал(а) и принимаю Политику конфиденциальности"),
    )

    accept_terms_of_use = forms.BooleanField(
        required=True,
        label=_("Я прочитал(а) и принимаю Правила использования сервиса"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "class": "form__control",
                "placeholder": "Email",
                "type": "email",
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form__control",
                "placeholder": "Пароль",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form__control",
                "placeholder": "Подтверждение пароля",
            }
        )

        self.fields["accept_privacy_policy"].widget.attrs.update(
            {
                "class": "legal-accept__checkbox",
            }
        )

        self.fields["accept_terms_of_use"].widget.attrs.update(
            {
                "class": "legal-accept__checkbox",
            }
        )

    def clean(self):
        """
        Проверяет согласия после стандартной валидации allauth.
        """
        cleaned_data = super().clean()

        if not cleaned_data.get("accept_privacy_policy"):
            self.add_error(
                "accept_privacy_policy",
                _(
                    "Для регистрации необходимо принять "
                    "Политику конфиденциальности."
                ),
            )

        if not cleaned_data.get("accept_terms_of_use"):
            self.add_error(
                "accept_terms_of_use",
                _(
                    "Для регистрации необходимо принять "
                    "Правила использования сервиса."
                ),
            )

        return cleaned_data

    def save(self, request):
        """
        Создаёт пользователя, сохраняет имя
        и фиксирует явно данные согласия.
        """
        user = super().save(request)

        user.first_name = self.cleaned_data.get("first_name", "")
        user.save()

        self.save_consents(
            request=request,
            user=user,
        )

        return user


class CustomLoginForm(LoginForm):
    """
    Форма входа по email + пароль.

    Используется только для авторизации
    уже существующего пользователя.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.social_redirect_email = None

        self.fields["login"].widget.attrs.update(
            {
                "class": "form__control",
                "placeholder": "Email",
                "type": "email",
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "class": "form__control",
                "placeholder": "Пароль",
            }
        )

    def clean(self):
        """
        Если пользователь существует, но не имеет пароля
        и создан через Google/Yandex, блокируем email-вход
        и передаём view email для перенаправления
        на страницу авторизации.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        login = self.cleaned_data.get("login")

        if login:
            try:
                user = User.objects.get(email__iexact=login)

                if (
                    not user.has_usable_password()
                    and user.socialaccount_set.exists()
                ):
                    self.social_redirect_email = user.email

                    self.add_error(
                        None,
                        "SOCIAL_ONLY_ACCOUNT",
                    )

                    return self.cleaned_data

            except User.DoesNotExist:
                pass

        return super().clean()


class CustomSocialSignupForm(ConsentMixin, SocialSignupForm):
    """
    Форма завершения регистрации через Google/Yandex.

    Появляется только если пользователь ещё не зарегистрирован,
    потому что SOCIALACCOUNT_AUTO_SIGNUP = False.
    """

    consent_source = UserLegalConsent.ConsentSource.SOCIAL_SIGNUP

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form__control",
                "type": "email",
                "readonly": True,
            }
        ),
        label=_("Email"),
    )

    accept_privacy_policy = forms.BooleanField(
        required=True,
        label=_("Я прочитал(а) и принимаю Политику конфиденциальности"),
    )

    accept_terms_of_use = forms.BooleanField(
        required=True,
        label=_("Я прочитал(а) и принимаю Правила использования сервиса"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].initial = (
            self.sociallogin.email_addresses[0].email
            if self.sociallogin.email_addresses
            else ""
        )

    def clean(self):
        """
        Проверяет явное согласие пользователя.
        """
        cleaned_data = super().clean()

        if not cleaned_data.get("accept_privacy_policy"):
            self.add_error(
                "accept_privacy_policy",
                _(
                    "Для регистрации необходимо принять "
                    "Политику конфиденциальности."
                ),
            )

        if not cleaned_data.get("accept_terms_of_use"):
            self.add_error(
                "accept_terms_of_use",
                _(
                    "Для регистрации необходимо принять "
                    "Правила использования сервиса."
                ),
            )

        return cleaned_data

    def save(self, request):
        """
        Завершает социальную регистрацию
        и фиксирует явно данные согласия.
        """
        user = super().save(request)

        self.save_consents(
            request=request,
            user=user,
        )

        return user


class CustomResetPasswordForm(ResetPasswordForm):
    """
    Форма восстановления пароля.

    Разрешает сброс пароля пользователям,
    созданным через Google/Yandex.
    """

    def get_users(self, email):
        """
        Возвращает активных пользователей для отправки письма.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        active_users = User.objects.filter(
            email__iexact=email,
            is_active=True,
        )

        return (
            user
            for user in active_users
            if user.has_usable_password()
            or user.socialaccount_set.exists()
        )