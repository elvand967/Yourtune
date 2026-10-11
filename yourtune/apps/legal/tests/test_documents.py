# apps/legal/tests/test_documents.py
# ====================================

import uuid

from django.test import TestCase

from apps.legal.models import (
    LegalDocument,
    LegalDocumentVersion,
    UserLegalConsent,
)
from apps.legal.services import LegalDocumentService


class LegalDocumentModelTests(TestCase):
    """
    Тесты модели LegalDocument.
    """

    def setUp(self):
        self.document = LegalDocument.objects.create(
            document_type=LegalDocument.DocumentType.PRIVACY_POLICY,
            title="Политика конфиденциальности сервиса YourTune",
            description="Политика обработки персональных данных.",
        )

    def test_slug_generated_automatically(self):
        """
        При сохранении документа без slug
        он должен создаваться автоматически.
        """
        self.assertTrue(self.document.slug)
        self.assertNotEqual(self.document.slug, "")

    def test_manual_slug_is_not_overwritten(self):
        """
        Вручную заданный slug не должен перезаписываться
        при повторном сохранении документа.
        """
        self.document.slug = "privacy-policy-custom"
        self.document.save()

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.slug,
            "privacy-policy-custom",
        )

    def test_slug_is_unique(self):
        """
        При создании второго документа с одинаковым названием
        slug должен получить числовой суффикс.
        """
        second_document = LegalDocument.objects.create(
            document_type=LegalDocument.DocumentType.TERMS_OF_USE,
            title=self.document.title,
        )

        self.assertNotEqual(
            second_document.slug,
            self.document.slug,
        )

        self.assertTrue(
            second_document.slug.startswith(self.document.slug),
        )

    def test_slug_fallback_for_empty_title(self):
        """
        Если title пустой или slugify_seo вернул пустую строку,
        должен быть создан fallback slug.
        """
        document = LegalDocument(
            document_type=LegalDocument.DocumentType.TERMS_OF_USE,
            title="",
        )

        document.slug = document._generate_unique_slug()
        document.save()

        self.assertTrue(document.slug)

    def test_get_current_version_returns_none_initially(self):
        """
        У нового документа не должно быть актуальной версии.
        """
        self.assertIsNone(
            self.document.get_current_version(),
        )


class LegalDocumentVersionTests(TestCase):
    """
    Тесты версий юридических документов.
    """

    def setUp(self):
        self.document = LegalDocument.objects.create(
            document_type=LegalDocument.DocumentType.PRIVACY_POLICY,
            title="Политика конфиденциальности",
        )

        self.version = LegalDocumentVersion.objects.create(
            document=self.document,
            version="1.0",
            title="Первая версия политики",
            content="<p>Текст политики.</p>",
        )

    def test_version_is_not_published_by_default(self):
        """
        Новая версия не должна быть опубликована.
        """
        self.assertFalse(self.version.is_published)
        self.assertIsNone(self.version.published_at)

    def test_publish_sets_current_version(self):
        """
        После публикации версия должна стать актуальной.
        """
        self.version.publish()

        self.document.refresh_from_db()

        self.assertTrue(self.version.is_published)
        self.assertIsNotNone(self.version.published_at)
        self.assertEqual(
            self.document.current_version,
            self.version,
        )

    def test_publish_keeps_previous_version_in_history(self):
        """
        При публикации новой версии предыдущая
        должна остаться опубликованной, но перестать быть актуальной.
        """
        first_version = self.version
        first_version.publish()

        second_version = LegalDocumentVersion.objects.create(
            document=self.document,
            version="1.1",
            title="Обновлённая политика",
            content="<p>Обновлённый текст политики.</p>",
        )

        second_version.publish()

        first_version.refresh_from_db()
        second_version.refresh_from_db()
        self.document.refresh_from_db()

        self.assertTrue(first_version.is_published)
        self.assertTrue(second_version.is_published)

        self.assertEqual(
            self.document.current_version,
            second_version,
        )

    def test_unpublish_clears_current_version(self):
        """
        После снятия с публикации актуальной версии
        документ не должен иметь current_version.
        """
        self.version.publish()
        self.version.unpublish()

        self.document.refresh_from_db()

        self.assertFalse(self.version.is_published)
        self.assertIsNone(self.document.current_version)

    def test_unpublished_version_cannot_be_current(self):
        """
        Если актуальная версия снята с публикации,
        ссылка document.current_version должна сброситься.
        """
        self.version.publish()

        self.version.is_published = False
        self.version.save()

        self.document.refresh_from_db()

        self.assertIsNone(self.document.current_version)

    def test_document_version_unique_constraint(self):
        """
        Нельзя создать две версии с одинаковым номером
        для одного документа.
        """
        self.version.publish()

        duplicate_version = LegalDocumentVersion(
            document=self.document,
            version="1.0",
            title="Дубликат версии",
            content="<p>Дубликат.</p>",
        )

        with self.assertRaises(Exception):
            duplicate_version.save()


class LegalDocumentServiceTests(TestCase):
    """
    Тесты сервиса LegalDocumentService.
    """

    def setUp(self):
        self.document = LegalDocument.objects.create(
            document_type=LegalDocument.DocumentType.PRIVACY_POLICY,
            title="Политика конфиденциальности",
        )

        self.version = LegalDocumentVersion.objects.create(
            document=self.document,
            version="1.0",
            title="Первая версия политики",
            content="<p>Текст политики.</p>",
        )

    def test_get_document_by_type(self):
        """
        Сервис должен находить активный документ по типу.
        """
        document = LegalDocumentService.get_document_by_type(
            LegalDocument.DocumentType.PRIVACY_POLICY,
        )

        self.assertEqual(
            document,
            self.document,
        )

    def test_get_published_version(self):
        """
        Сервис должен возвращать опубликованную версию документа.
        """
        self.version.publish()

        version = LegalDocumentService.get_published_version(
            self.document,
        )

        self.assertEqual(
            version,
            self.version,
        )

    def test_get_published_version_returns_none_without_publication(self):
        """
        Если версия не опубликована,
        сервис не должен возвращать её как актуальную.
        """
        version = LegalDocumentService.get_published_version(
            self.document,
        )

        self.assertIsNone(version)

    def test_pending_documents_for_anonymous_user(self):
        """
        Для неавторизованного пользователя
        ожидающих документов быть не должно.
        """
        self.version.publish()

        pending_documents = LegalDocumentService.get_pending_documents(
            user=None,
        )

        self.assertEqual(
            pending_documents,
            [],
        )

    def test_pending_documents_for_user_without_consent(self):
        """
        Для авторизованного пользователя без согласия
        документ должен находиться в списке ожидающих.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
        )

        self.version.publish()

        pending_documents = LegalDocumentService.get_pending_documents(
            user=user,
        )

        self.assertIn(
            self.document,
            pending_documents,
        )

    def test_accept_documents_creates_consent(self):
        """
        После принятия документа должна создаваться
        запись пользовательского согласия.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
        )

        self.version.publish()

        accepted_versions = LegalDocumentService.accept_documents(
            user=user,
            request=None,
            documents=[self.document],
            source=UserLegalConsent.ConsentSource.REQUIRED_REVIEW,
        )

        self.assertEqual(
            accepted_versions,
            [self.version],
        )

        self.assertTrue(
            UserLegalConsent.objects.filter(
                user=user,
                document_version=self.version,
            ).exists()
        )

    def test_accept_documents_by_types(self):
        """
        Метод accept_documents_by_types должен создавать согласие
        на актуальную опубликованную версию документа.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
        )

        self.version.publish()

        accepted_versions = LegalDocumentService.accept_documents_by_types(
            user=user,
            request=None,
            document_types=[
                LegalDocument.DocumentType.PRIVACY_POLICY,
            ],
            source=UserLegalConsent.ConsentSource.SIGNUP,
        )

        self.assertEqual(
            accepted_versions,
            [self.version],
        )

        self.assertTrue(
            UserLegalConsent.objects.filter(
                user=user,
                document_version=self.version,
                source=UserLegalConsent.ConsentSource.SIGNUP,
            ).exists()
        )

    def test_has_pending_documents_false_after_accept(self):
        """
        После принятия документа
        у пользователя не должно быть ожидающих документов.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
        )

        self.version.publish()

        LegalDocumentService.accept_documents_by_types(
            user=user,
            request=None,
            document_types=[
                LegalDocument.DocumentType.PRIVACY_POLICY,
            ],
        )

        self.assertFalse(
            LegalDocumentService.has_pending_documents(user),
        )