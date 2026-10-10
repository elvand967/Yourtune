
# apps/legal/mixins/consent.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

from apps.legal.services import LegalDocumentService


class ConsentRequiredMixin(LoginRequiredMixin):
    """
    Требует принятия всех актуальных обязательных
    юридических документов.

    Подключать только к защищённым разделам:
    - профиль;
    - плейлисты;
    - избранное;
    - настройки;
    - интеграции.

    Не подключать к:
    - входу;
    - регистрации;
    - странице согласия;
    - публичным политике и правилам.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(
                request,
                *args,
                **kwargs,
            )

        pending_documents = LegalDocumentService.get_pending_documents(
            request.user,
        )

        if pending_documents:
            return redirect(
                f"{reverse('legal:required_consent')}"
                f"?next={request.get_full_path()}"
            )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )