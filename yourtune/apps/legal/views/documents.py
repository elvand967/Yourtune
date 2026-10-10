# apps/legal/views/documents.py

from django.http import Http404
from django.shortcuts import render
from django.views import View

from apps.legal.models import LegalDocument
from apps.legal.services import LegalDocumentService


class LegalDocumentDetailView(View):
    """
    Публичная страница юридического документа.

    Отображает актуальную опубликованную версию документа.
    """

    template_name = "legal/base_document.html"
    document_type = None
    fallback_title = ""
    fallback_description = ""

    def get(self, request, *args, **kwargs):
        document = LegalDocumentService.get_document_by_type(
            self.document_type,
        )

        version = LegalDocumentService.get_published_version(
            document,
        )

        if not version:
            raise Http404("Документ пока не опубликован.")

        context = {
            "document": document,
            "version": version,
            "title": version.title or self.fallback_title,
            "description": (
                document.description
                or self.fallback_description
            ),
            "content": version.content,
            "published_at": version.published_at,
        }

        return render(
            request,
            self.template_name,
            context,
        )


class PolicyDetailView(LegalDocumentDetailView):
    """
    Публичная страница политики конфиденциальности.
    """

    document_type = LegalDocument.DocumentType.PRIVACY_POLICY
    template_name = "legal/policy.html"
    fallback_title = "Политика конфиденциальности"
    fallback_description = (
        "Политика конфиденциальности платформы YourTune."
    )


class TermsDetailView(LegalDocumentDetailView):
    """
    Публичная страница правил использования сервиса.
    """

    document_type = LegalDocument.DocumentType.TERMS_OF_USE
    template_name = "legal/rules.html"
    fallback_title = "Правила использования сервиса"
    fallback_description = (
        "Правила использования платформы YourTune."
    )