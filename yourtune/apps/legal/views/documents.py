
# apps/legal/views/documents.py
# ================================

from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from apps.legal.models import LegalDocument
from apps.legal.services import LegalDocumentService


class LegalDocumentDetailView(View):
    """
    Публичная страница активного юридического документа.

    Отображает актуальную опубликованную версию документа
    по его slug.
    """

    template_name = "legal/document_detail.html"

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        document = (
            LegalDocument.objects
            .filter(
                slug=slug,
                is_active=True,
            )
            .first()
        )

        if not document:
            raise Http404("Документ не найден.")

        version = LegalDocumentService.get_published_version(
            document,
        )

        if not version:
            raise Http404("Документ пока не опубликован.")

        context = {
            "document": document,
            "version": version,
            "title": version.title or document.title,
            "description": document.description,
            "content": version.content,
            "published_at": version.published_at,
        }

        return render(
            request,
            self.template_name,
            context,
        )


class LegalDocumentListView(ListView):
    """
    Список активных юридических документов YourTune.
    """

    template_name = "legal/document_list.html"
    context_object_name = "documents"

    def get_queryset(self):
        return (
            LegalDocument.objects
            .filter(is_active=True)
            .order_by(
                "menu_order",
                "title",
            )
        )