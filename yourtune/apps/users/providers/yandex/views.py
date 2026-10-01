
# apps/users/providers/yandex/views.py

from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView


class YandexLoginView(OAuth2LoginView):
    pass


class YandexCallbackView(OAuth2CallbackView):
    pass