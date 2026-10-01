# apps/users/forms/auth.py

from django import forms
from allauth.account.forms import SignupForm, LoginForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class CustomSignupForm(SignupForm):
    """Кастомная форма регистрации с email и паролем."""

    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form__control',
            'placeholder': 'Имя',
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form__control',
            'placeholder': 'Фамилия',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Переопределяем виджет email
        self.fields['email'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Email',
            'type': 'email',
        })
        # Переопределяем виджет пароля
        self.fields['password1'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Подтверждение пароля',
        })

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()
        return user


class CustomLoginForm(LoginForm):
    """Кастомная форма входа."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Email',
            'type': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form__control',
            'placeholder': 'Пароль',
        })


class CustomSocialSignupForm(SocialSignupForm):
    """Форма завершения регистрации через соц. сеть."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form__control',
            'type': 'email',
            'readonly': True,
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.sociallogin.email_addresses:
            self.fields['email'].initial = self.sociallogin.email_addresses[0].email