# apps/users/adapters.py
# ======================

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Адаптер социальной аутентификации Google/Yandex.

    Важно:
    - существующий пользователь связывается по email;
    - новый пользователь НЕ создаётся автоматически;
    - для нового пользователя allauth откроет
      страницу завершения регистрации;
    - согласия создаёт CustomSocialSignupForm.
    """

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Запрещает автоматическую регистрацию.

        Благодаря этому новый пользователь
        попадает на CustomSocialSignupForm.
        """
        return False

    def is_open_for_signup(self, request, sociallogin):
        """
        Разрешает регистрацию через соцсеть,
        но только после явного завершения формы.
        """
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Связывает OAuth-аккаунт с существующим пользователем
        по email.

        Если пользователь не найден, ничего не делаем:
        allauth перенаправит на страницу
        завершения регистрации.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        provider = sociallogin.account.get_provider(request)
        common_fields = provider.extract_common_fields(
            sociallogin.account.extra_data,
        )

        email = common_fields.get("email")

        if not email and sociallogin.email_addresses:
            try:
                email = sociallogin.email_addresses.all()[0].email
            except (IndexError, AttributeError):
                email = None

        if not email:
            return

        try:
            user = User.objects.get(email__iexact=email)

            if not sociallogin.is_existing:
                sociallogin.user = user

            sociallogin.connect(request, user)

        except User.DoesNotExist:
            return


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Адаптер email-аутентификации.
    """

    def get_login_redirect_url(self, request):
        return super().get_login_redirect_url(request)

    def get_signup_redirect_url(self, request):
        return super().get_signup_redirect_url(request)