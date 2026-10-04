# apps/users/providers/yandex/provider.py
# =======================================
# Кастомный OAuth2-провайдер Yandex для django-allauth.
#
# Документация Yandex OAuth2:
# https://yandex.ru/dev/oauth/doc/dg/concepts/about.html

from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from .views import YandexCallbackView, YandexLoginView


class YandexProvider(OAuth2Provider):
    """
    Провайдер Yandex OAuth2.

    Все настройки (client_id, secret, scope) берутся из
    SOCIALACCOUNT_PROVIDERS['yandex']['APP'] в settings.py.
    """

    id = 'yandex'
    name = 'Yandex'

    def get_default_scope(self):
        """Запрашиваемые разрешения."""
        return ['login:email', 'login:info']

    def extract_uid(self, data):
        """Уникальный идентификатор пользователя Yandex."""
        return str(data.get('id'))

    def extract_common_fields(self, data):
        """Стандартные поля пользователя из ответа Yandex."""
        return {
            'email': data.get('default_email') or data.get('emails', [None])[0],
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
        }

    def get_login_view(self):
        """View начала OAuth2-flow."""
        return YandexLoginView

    def get_callback_view(self):
        """View обработки callback."""
        return YandexCallbackView


provider_classes = [YandexProvider]