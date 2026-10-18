
# apps/notifications/services/notify.py

"""
Единая точка входа уведомлений Yourtune.

Примеры:

    from apps.notifications.services import Notify
    from apps.notifications.categories import Category

    Notify.success(
        request,
        title=_("Профиль обновлён"),
        persist=False,
        category=Category.ACCOUNT,
    )

    Notify.warning(
        request,
        title=_("Подтвердите email"),
        message=_("Письмо отправлено"),
        category=Category.SECURITY,
        url=reverse("account_email"),
    )

    Notify.info(
        None,
        title=_("Новая версия соглашения"),
        user=user,
        category=Category.LEGAL,
    )
"""

import logging

from django.contrib import messages
from django.db import transaction
from django.utils.html import format_html

from apps.notifications.categories import MANDATORY_CATEGORIES, Category
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)

Level = Notification.Level

_MESSAGE_LEVELS = {
    Level.SUCCESS: messages.SUCCESS,
    Level.INFO: messages.INFO,
    Level.WARNING: messages.WARNING,
    Level.ERROR: messages.ERROR,
}


class Notify:
    """Фасад для отправки toast-сообщений и сохранения уведомлений."""

    # ------------------------------------------------------------------ API

    @classmethod
    def send(
        cls,
        request=None,
        *,
        title,
        message="",
        level=Level.INFO,
        user=None,
        category=Category.SYSTEM,
        url="",
        toast=True,
        persist=True,
    ):
        """
        Отправляет уведомление.

        Аргументы:
            request   — текущий HTTP-запрос; нужен для toast.
            title     — обязательный заголовок уведомления.
            message   — дополнительный текст.
            level     — уровень из Notification.Level.
            user      — явный получатель; по умолчанию request.user.
            category  — категория из Category.
            url       — внутренняя ссылка для действия.
            toast     — показать всплывающее сообщение.
            persist   — сохранить уведомление в БД после коммита транзакции.
        """
        request_user = getattr(request, "user", None)
        recipient = user if user is not None else request_user

        if toast and request is not None:
            # Toast показываем только получателю, который видит текущий request.
            if recipient is None or recipient == request_user:
                cls._toast(request, level, title, message)

        if persist and recipient is not None and recipient.is_authenticated:
            if cls._is_enabled(recipient, category):
                cls._persist(
                    user=recipient,
                    level=level,
                    title=title,
                    message=message,
                    category=category,
                    url=url,
                )

    @classmethod
    def success(cls, request=None, *, title, message="", **kwargs):
        cls.send(
            request,
            title=title,
            message=message,
            level=Level.SUCCESS,
            **kwargs,
        )

    @classmethod
    def info(cls, request=None, *, title, message="", **kwargs):
        cls.send(
            request,
            title=title,
            message=message,
            level=Level.INFO,
            **kwargs,
        )

    @classmethod
    def warning(cls, request=None, *, title, message="", **kwargs):
        cls.send(
            request,
            title=title,
            message=message,
            level=Level.WARNING,
            **kwargs,
        )

    @classmethod
    def error(cls, request=None, *, title, message="", **kwargs):
        cls.send(
            request,
            title=title,
            message=message,
            level=Level.ERROR,
            **kwargs,
        )

    # ------------------------------------------------------------ internals

    @staticmethod
    def _toast(request, level, title, message):
        """
        Добавляет toast в django.contrib.messages.

        format_html() экранирует подставляемые значения, поэтому
        использовать фильтр |safe в шаблоне не нужно.
        """
        if message:
            text = format_html("<strong>{}</strong> {}", title, message)
        else:
            text = format_html("{}", title)

        messages.add_message(
            request,
            _MESSAGE_LEVELS[level],
            text,
            extra_tags="toast",
            fail_silently=True,
        )

    @staticmethod
    def _persist(user, level, title, message, category, url):
        """
        Сохраняет уведомление после успешного коммита текущей транзакции.

        Если основной запрос выполняется вне transaction.atomic(),
        callback выполнится сразу. Если транзакция откатится,
        уведомление создано не будет.
        """

        def _safe_create():
            try:
                Notification.objects.create(
                    user=user,
                    level=level,
                    title=str(title),
                    message=str(message),
                    category=category,
                    url=url,
                )
            except Exception:
                logger.exception(
                    "Не удалось сохранить уведомление: "
                    "user=%s, category=%s, title=%s",
                    getattr(user, "pk", None),
                    category,
                    title,
                )

        transaction.on_commit(_safe_create, robust=True)

    @staticmethod
    def _is_enabled(user, category):
        """
        Проверяет, разрешено ли пользователю получать уведомления категории.

        Обязательные категории нельзя отключить.
        """
        if category in MANDATORY_CATEGORIES:
            return True

        # TODO: этап 4 — учитывать настройки профиля пользователя.
        return True