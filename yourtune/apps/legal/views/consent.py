
# apps/legal/views/consent.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from apps.legal.forms import LegalConsentForm
from apps.legal.models import UserLegalConsent
from apps.legal.services import LegalDocumentService


class RequiredConsentView(LoginRequiredMixin, View):
    """
    Страница обязательного принятия актуальных
    юридических документов.
    """

    template_name = "legal/accept.html"

    def get_pending_documents(self):
        """
        Возвращает список документов, ожидающих принятия.
        """
        return LegalDocumentService.get_pending_documents(
            self.request.user,
        )

    def get(self, request, *args, **kwargs):
        documents = self.get_pending_documents()

        if not documents:
            return redirect(
                self.get_success_url(),
            )

        form = LegalConsentForm(
            documents=documents,
        )

        context = self.get_context_data(
            documents=documents,
            form=form,
        )

        return render(
            request,
            self.template_name,
            context,
        )

    def post(self, request, *args, **kwargs):
        documents = self.get_pending_documents()

        if not documents:
            return redirect(
                self.get_success_url(),
            )

        form = LegalConsentForm(
            data=request.POST,
            documents=documents,
        )

        if form.is_valid():
            LegalDocumentService.accept_documents(
                user=request.user,
                request=request,
                documents=documents,
                source=UserLegalConsent.ConsentSource.REQUIRED_REVIEW,
            )

            messages.success(
                request,
                "Спасибо! Юридические документы приняты.",
            )

            return redirect(
                self.get_success_url(),
            )

        messages.error(
            request,
            "Подтвердите принятие всех обязательных документов.",
        )

        context = self.get_context_data(
            documents=documents,
            form=form,
        )

        return render(
            request,
            self.template_name,
            context,
        )

    def get_context_data(self, documents, form):
        """
        Формирует контекст страницы согласия.
        """
        return {
            "documents": documents,
            "form": form,
            "title": "Примите условия сервиса",
            "description": (
                "Для использования личного кабинета YourTune "
                "необходимо ознакомиться с актуальными документами "
                "и подтвердить их принятие."
            ),
        }

    def get_success_url(self):
        """
        Возвращает пользователя на исходную страницу
        или в личный кабинет.
        """
        next_url = self.request.GET.get("next")

        if next_url:
            return next_url

        return reverse("users:profile_detail")