# apps/notifications/tests/test_notify.py
"""
Тесты сервиса уведомлений Notify и связанных view.

Запуск:  python manage.py test apps.notifications
"""

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.cookie import CookieStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.safestring import SafeData

from apps.notifications.models import Notification
from apps.notifications.services import Notify

# Ваша кастомная модель пользователя (без жёсткой привязки к имени класса)
User = get_user_model()


class NotifyTests(TestCase):
    """Каждый тест выполняется в транзакции, которая в конце откатывается."""

    @classmethod
    def setUpTestData(cls):
        # Создаётся ОДИН раз для всего класса — быстрее, чем перед каждым тестом
        cls.user = User.objects.create_user(email="u@example.com", password="pass12345")
        cls.other = User.objects.create_user(email="o@example.com", password="pass12345")

    # ------------------------------------------------------------ helpers

    def _make_request(self, user):
        """
        «Голый» запрос без middleware и view.
        _messages обычно ставит MessageMiddleware — здесь ставим вручную.
        CookieStorage выбран потому, что ему не нужна сессия.
        """
        request = RequestFactory().get("/")
        request.user = user
        request._messages = CookieStorage(request)
        return request

    # ------------------------------------------------- запись в историю

    def test_persist_without_request(self):
        """Без request (сигналы, фоновые задачи) уведомление пишется в БД."""
        # Notify пишет через transaction.on_commit. В TestCase коммита нет,
        # поэтому перехватываем отложенные функции и выполняем их вручную.
        with self.captureOnCommitCallbacks(execute=True):
            Notify.info(None, "Тест", "Текст", user=self.user)

        self.assertEqual(self.user.notifications.count(), 1)

    def test_persist_false_skips_db(self):
        """persist=False — только toast, в историю ничего не попадает."""
        with self.captureOnCommitCallbacks(execute=True):
            Notify.success(None, "Тест", user=self.user, persist=False)

        self.assertFalse(Notification.objects.exists())

    # ------------------------------------------------------------ toast

    def test_toast_shown_to_self(self):
        """Уведомление самому себе: toast есть И запись в истории есть."""
        request = self._make_request(self.user)

        with self.captureOnCommitCallbacks(execute=True):
            Notify.info(request, "Себе")

        texts = [str(m) for m in get_messages(request)]
        self.assertTrue(any("Себе" in t for t in texts))
        self.assertEqual(self.user.notifications.count(), 1)

    def test_toast_not_shown_for_other_recipient(self):
        """
        Действие выполняет self.user, а уведомление адресовано self.other:
        toast у self.user НЕТ, запись в истории у self.other ЕСТЬ.
        """
        request = self._make_request(self.user)

        with self.captureOnCommitCallbacks(execute=True):
            Notify.info(request, "Для другого", user=self.other)

        self.assertEqual(len(list(get_messages(request))), 0)
        self.assertEqual(self.other.notifications.count(), 1)
        self.assertEqual(self.user.notifications.count(), 0)

    def test_toast_escapes_html(self):
        """Пользовательский HTML экранируется, наша разметка — нет."""
        request = self._make_request(self.user)

        Notify.error(request, "<script>x</script>", "<b>текст</b>", persist=False)

        message = list(get_messages(request))[-1]
        text = str(message)

        self.assertIn("&lt;script&gt;", text)               # данные экранированы
        self.assertIn("&lt;b&gt;текст&lt;/b&gt;", text)
        self.assertIn("<strong>", text)                     # разметка format_html сохранена
        self.assertIsInstance(message.message, SafeData)    # |safe в шаблоне не нужен
        self.assertIn("toast", message.tags)                # extra_tags на месте

    # ------------------------------------------------------------ views

    def test_mark_all_read_does_not_create_new_notification(self):
        """«Прочитать все» не должно порождать новое непрочитанное уведомление."""
        with self.captureOnCommitCallbacks(execute=True):
            Notify.warning(None, "Непрочитанное", user=self.user)

        self.client.force_login(self.user)  # вход без формы и пароля
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("notifications:mark_all_read"))

        self.assertEqual(self.user.notifications.count(), 1)
        self.assertFalse(self.user.notifications.unread().exists())

    # ------------------------------------------------------------ model

    def test_read_requires_read_at(self):
        """is_read=True без read_at (как галочка в админке) — save() сам ставит дату."""
        n = Notification.objects.create(user=self.user, title="X")
        n.is_read = True
        n.save()
        n.refresh_from_db()  # проверяем то, что реально лежит в БД

        self.assertIsNotNone(n.read_at)