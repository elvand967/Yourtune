
# apps/core/views/__init__.py

"""
Пакет views приложения core.

Каждая группа представлений размещается в отдельном модуле,
а публичные view-функции и классы импортируются здесь.
Это позволяет использовать понятные импорты:

from apps.core.views import cookie_consent_api
"""

from .cookie_consent import cookie_consent_api

__all__ = (
    "cookie_consent_api",
)