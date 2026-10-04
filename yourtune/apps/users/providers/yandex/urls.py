# apps/users/providers/yandex/urls.py
# ===================================
# URL-маршруты для Yandex OAuth2.
#
# Эти URL подключаются allauth автоматически
# через YandexProvider.get_urls().
#
# Итоговые адреса:
# - /users/accounts/yandex/login/           — начало OAuth2-flow
# - /users/accounts/yandex/login/callback/  — callback от Yandex

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2LoginView,
    OAuth2CallbackView,
)
from django.urls import path

from .provider import YandexProvider

# URL-имена обязаны быть: <provider_id>_login и <provider_id>_callback
# Именно по ним {% provider_login_url 'yandex' %} строит ссылку.
urlpatterns = [
    path(
        'login/',
        OAuth2LoginView.adapter_view(YandexProvider),
        name='yandex_login',
    ),
    path(
        'login/callback/',
        OAuth2CallbackView.adapter_view(YandexProvider),
        name='yandex_callback',
    ),
]