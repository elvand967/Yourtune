
# apps/legal/services/documents.py
# ==================================

from django.db.models import Prefetch

from apps.legal.models import (
    LegalDocument,
    LegalDocumentVersion,
    UserLegalConsent,
)


class LegalDocumentService:
    """
    Сервис работы с юридическими документами,
    их версиями и пользовательскими согласиями.
    """

    # =========================================================
    # Получение документов и версий
    # =========================================================

    @staticmethod
    def get_document_by_type(document_type):
        """
        Возвращает активный документ заданного типа.

        Пример:
        LegalDocumentService.get_document_by_type(
            LegalDocument.DocumentType.PRIVACY_POLICY
        )
        """
        return (
            LegalDocument.objects
            .filter(
                document_type=document_type,
                is_active=True,
            )
            .first()
        )

    @staticmethod
    def get_published_version(document):
        """
        Возвращает актуальную опубликованную версию документа.
        """
        if not document:
            return None

        version = document.get_current_version()

        if version and version.is_published:
            return version

        return (
            LegalDocumentVersion.objects
            .filter(
                document=document,
                is_published=True,
            )
            .order_by("-published_at", "-created_at")
            .first()
        )

    @classmethod
    def get_policy_version(cls):
        """
        Возвращает актуальную версию политики конфиденциальности.
        """
        document = cls.get_document_by_type(
            LegalDocument.DocumentType.PRIVACY_POLICY,
        )

        return cls.get_published_version(document)

    @classmethod
    def get_terms_version(cls):
        """
        Возвращает актуальную версию правил использования сервиса.
        """
        document = cls.get_document_by_type(
            LegalDocument.DocumentType.TERMS_OF_USE,
        )

        return cls.get_published_version(document)

    @staticmethod
    def get_active_required_documents():
        """
        Возвращает активные обязательные документы
        с назначенной актуальной версией.
        """
        return (
            LegalDocument.objects
            .filter(
                is_active=True,
                is_required=True,
                current_version__isnull=False,
            )
            .select_related("current_version")
        )

    @staticmethod
    def get_documents_with_current_versions():
        """
        Возвращает активные документы и их актуальные версии.

        Используется для публичных страниц, меню и футера.
        """
        return (
            LegalDocument.objects
            .filter(
                is_active=True,
                current_version__isnull=False,
            )
            .select_related("current_version")
            .prefetch_related(
                Prefetch(
                    "versions",
                    queryset=LegalDocumentVersion.objects.filter(
                        is_published=True,
                    ).order_by("-published_at"),
                )
            )
        )

    @classmethod
    def get_documents_by_types(cls, document_types):
        """
        Возвращает активные документы указанных типов,
        имеющие актуальную опубликованную версию.

        Пример:
        LegalDocumentService.get_documents_by_types(
            [
                LegalDocument.DocumentType.PRIVACY_POLICY,
                LegalDocument.DocumentType.TERMS_OF_USE,
            ]
        )
        """
        documents = []

        for document_type in document_types:
            document = cls.get_document_by_type(document_type)

            if not document:
                continue

            version = cls.get_published_version(document)

            if version:
                documents.append(document)

        return documents

    # =========================================================
    # Проверка и создание согласий
    # =========================================================

    @staticmethod
    def get_pending_documents(user):
        """
        Возвращает список активных обязательных документов,
        актуальные версии которых пользователь ещё не принял.

        Возвращается list, а не QuerySet:
        согласие проверяется для каждой актуальной версии.
        """
        if not user or not user.is_authenticated:
            return []

        required_documents = (
            LegalDocumentService
            .get_active_required_documents()
        )

        pending_documents = []

        for document in required_documents:
            version = document.current_version

            if not version or not version.is_published:
                continue

            has_consent = UserLegalConsent.has_accepted_version(
                user=user,
                document_version=version,
            )

            if not has_consent:
                pending_documents.append(document)

        return pending_documents

    @staticmethod
    def has_pending_documents(user):
        """
        Проверяет, есть ли у пользователя документы,
        требующие принятия.
        """
        return bool(
            LegalDocumentService.get_pending_documents(user),
        )

    @staticmethod
    def accept_documents(
        user,
        request,
        documents,
        source=UserLegalConsent.ConsentSource.REQUIRED_REVIEW,
    ):
        """
        Создаёт согласия пользователя на актуальные версии
        переданных документов.

        Возвращает список принятых версий.
        """
        if not user or not user.is_authenticated:
            return []

        accepted_versions = []

        for document in documents:
            version = document.current_version

            if not version or not version.is_published:
                continue

            consent, created = UserLegalConsent.accept_version(
                user=user,
                document_version=version,
                request=request,
                source=source,
            )

            accepted_versions.append(version)

        return accepted_versions

    @classmethod
    def accept_documents_by_types(
        cls,
        user,
        request,
        document_types,
        source=UserLegalConsent.ConsentSource.SIGNUP,
    ):
        """
        Создаёт согласия пользователя на актуальные версии
        документов указанных типов.

        Используется при регистрации:
        - по email;
        - через Google/Yandex.
        """
        documents = cls.get_documents_by_types(document_types)

        return cls.accept_documents(
            user=user,
            request=request,
            documents=documents,
            source=source,
        )

    @staticmethod
    def accept_document(
        user,
        request,
        document,
        source=UserLegalConsent.ConsentSource.REQUIRED_REVIEW,
    ):
        """
        Создаёт согласие пользователя на актуальную версию
        одного документа.

        Возвращает кортеж:
        (принятая версия или None, создано ли новое согласие).
        """
        if not user or not user.is_authenticated:
            return None, False

        version = document.current_version

        if not version or not version.is_published:
            return None, False

        return UserLegalConsent.accept_version(
            user=user,
            document_version=version,
            request=request,
            source=source,
        )