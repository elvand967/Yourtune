# apps/users/providers/yandex/apps.py
# ===================================
# Конфигурация Django-приложения провайдера Yandex.
#
# Импорт provider.py происходит в ready(),
# когда реестр приложений уже готов.

from django.apps import AppConfig


class YandexProviderConfig(AppConfig):
    """Конфигурация приложения кастомного провайдера Yandex."""

    name = 'apps.users.providers.yandex'
    label = 'users_yandex_provider'
    verbose_name = 'Yandex OAuth2 Provider'

    def ready(self):
        """
        Импортируем provider, чтобы allauth зарегистрировал
        провайдер и его URL-ы (yandex_login, yandex_callback).
        """
        from . import provider  # noqa: F401