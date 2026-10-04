# apps/users/adapters.py
# ======================
# Кастомные адаптеры django-allauth.
#
# Назначение:
# 1. CustomSocialAccountAdapter — автоматическое связывание
#    соц. аккаунтов (Google/Yandex) с существующими пользователями по email.
# 2. CustomAccountAdapter — базовый адаптер email-аутентификации.
#
# ВАЖНО: get_user_model() вызывается ВНУТРИ методов,
# а не на уровне модуля. Это предотвращает ошибку
# AppRegistryNotReady при импорте адаптеров через settings.
#
# Пользователи, зарегистрированные ТОЛЬКО через соц. сеть,
# имеют unusable password. Они могут:
# - входить через Google/Yandex;
# - восстановить пароль по email (см. CustomResetPasswordForm);
# - после восстановления входить и по email+пароль.

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Адаптер для социальной аутентификации (Google, Yandex).

    Основная задача — связать соц. аккаунт с существующим
    пользователем по email, чтобы не создавать дубликаты.
    """

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Разрешаем автоматическую регистрацию.

        Если пользователь с таким email не найден,
        allauth создаст нового пользователя без формы.
        """
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Вызывается ПОСЛЕ успешной авторизации у провайдера,
        НО ДО создания/входа пользователя.

        Логика:
        1. Получаем email из данных провайдера.
        2. Ищем пользователя с таким email.
        3. Если найден — связываем соц. аккаунт с ним.
        4. Если не найден — allauth создаст нового
           (благодаря is_auto_signup_allowed = True).
        """
        # ✅ Ленивый импорт: get_user_model() вызывается
        # только при обработке запроса, когда приложения уже загружены
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Email из extra_data провайдера (Google/Yandex возвращают его)
        email = sociallogin.account.extra_data.get('email')

        # Fallback: если email нет в extra_data,
        # берём из списка email_addresses
        if not email:
            email = (
                sociallogin.email_addresses[0].email
                if sociallogin.email_addresses
                else None
            )

        if not email:
            return

        # Ищем пользователя (регистр email не важен)
        try:
            user = User.objects.get(email__iexact=email)

            # Связываем соц. аккаунт с существующим пользователем.
            # После этого user.socialaccount_set будет содержать этот аккаунт.
            sociallogin.connect(request, user)

        except User.DoesNotExist:
            # Пользователя нет — allauth создаст нового.
            # Пароль при этом будет unusable (set_unusable_password).
            pass


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Адаптер для email-аутентификации (регистрация, вход, сброс пароля).

    Используется allauth для всех операций с обычными
    (email+пароль) пользователями.
    """

    def get_login_redirect_url(self, request):
        """
        URL после успешного входа.

        По умолчанию берётся из LOGIN_REDIRECT_URL.
        Можно переопределить для сложной логики
        (например, редирект на страницу, с которой пришёл пользователь).
        """
        return super().get_login_redirect_url(request)

    def get_signup_redirect_url(self, request):
        """
        URL после успешной регистрации.
        """
        return super().get_signup_redirect_url(request)