# apps/users/providers/yandex/views.py
# ====================================
# Views для OAuth2-flow Yandex.
#
# allauth использует эти классы для:
# - YandexLoginView    — редирект пользователя на OAuth-страницу Yandex
# - YandexCallbackView — обработка ответа Yandex после авторизации

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2LoginView,
    OAuth2CallbackView,
)


class YandexLoginView(OAuth2LoginView):
    """
    Начало OAuth2-flow: редирект на authorize-URL Yandex.

    allauth автоматически подставит client_id, redirect_uri,
    scope и state из настроек SOCIALACCOUNT_PROVIDERS.
    """
    pass


class YandexCallbackView(OAuth2CallbackView):
    """
    Обработка callback от Yandex.

    allauth обменяет code на access_token,
    получит данные пользователя и вызовет адаптер
    (CustomSocialAccountAdapter.pre_social_login).
    """
    pass