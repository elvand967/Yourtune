
# apps/users/providers/yandex/provider.py

from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class YandexProvider(OAuth2Provider):
    id = 'yandex'
    name = 'Yandex'
    oauth2_version = '2'

    def get_default_scope(self):
        return ['login:email', 'login:info']

    def extract_uid(self, data):
        return str(data.get('id'))

    def extract_common_fields(self, data):
        return {
            'email': data.get('default_email') or data.get('emails', [None])[0],
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
        }


provider_classes = [YandexProvider]