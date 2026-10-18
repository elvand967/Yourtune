
# apps/notifications/categories.py


"""
Справочник категорий уведомлений.
Новая категория добавляется только здесь (+ makemigrations, т.к. меняются choices).
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.TextChoices):
    SYSTEM = "system", _("Системные")
    ACCOUNT = "account", _("Аккаунт и профиль")
    SECURITY = "security", _("Безопасность")
    LEGAL = "legal", _("Документы и согласия")
    CONTENT = "content", _("Избранное и плейлисты")


# Категории, которые пользователь не может отключить в настройках (этап 4)
MANDATORY_CATEGORIES = frozenset({
    Category.SYSTEM,
    Category.SECURITY,
    Category.LEGAL,
})