# apps/notifications/tests/test_notifications.py

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from apps.notifications.categories import Category
from apps.notifications.models import Notification
from apps.notifications.services import Notify

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="test-password-123",
        )

    def test_mark_as_read_sets_read_at(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Тест",
            category=Category.SYSTEM,
        )

        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)

        notification.mark_as_read()
        notification.refresh_from_db()

        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)

    def test_mark_read_bulk_update(self):
        Notification.objects.create(
            user=self.user,
            title="Первое",
            category=Category.SYSTEM,
        )
        Notification.objects.create(
            user=self.user,
            title="Второе",
            category=Category.SYSTEM,
        )

        updated = Notification.objects.for_user(self.user).mark_read()

        self.assertEqual(updated, 2)
        self.assertEqual(
            Notification.objects.for_user(self.user).unread().count(),
            0,
        )


class NotifyServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notify-tester",
            password="test-password-123",
        )

    def test_persist_creates_notification_after_commit(self):
        with self.captureOnCommitCallbacks(execute=True):
            Notify.info(
                None,
                title="Сервис работает",
                message="Проверка on_commit.",
                user=self.user,
                category=Category.SYSTEM,
                toast=False,
            )

        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                title="Сервис работает",
            ).exists()
        )

    def test_persist_false_does_not_create_notification(self):
        Notify.success(
            None,
            title="Только toast",
            user=self.user,
            persist=False,
        )

        self.assertFalse(
            Notification.objects.filter(title="Только toast").exists()
        )