
# apps/users/adapters.py


from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Адаптер для автоматического связывания соц. аккаунтов с существующими по email."""

    def is_auto_signup_allowed(self, request, sociallogin):
        """Разрешаем автоматическую регистрацию для всех."""
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Автоматически связываем соц. аккаунт с существующим пользователем по email.
        """
        email = sociallogin.account.extra_data.get('email')
        if not email:
            email = sociallogin.email_addresses[0].email if sociallogin.email_addresses else None

        if not email:
            return

        # Ищем пользователя с таким email
        try:
            user = User.objects.get(email__iexact=email)
            # Связываем соц. аккаунт с существующим пользователем
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            # Если пользователя нет — создаём нового (автоматическая регистрация)
            pass