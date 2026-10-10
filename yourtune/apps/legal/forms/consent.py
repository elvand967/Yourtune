
# apps/legal/forms/consent.py

from django import forms
from django.utils.translation import gettext_lazy as _


class LegalConsentForm(forms.Form):
    """
    Форма принятия актуальных юридических документов.

    Для каждого ожидающего документа динамически
    создаётся отдельный обязательный чекбокс.
    """

    def __init__(self, *args, documents=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.documents = documents or []

        for document in self.documents:
            field_name = self.get_field_name(document)

            self.fields[field_name] = forms.BooleanField(
                required=True,
                label=_(
                    "Я прочитал(а) и принимаю «%(title)s»"
                    % {"title": document.title}
                ),
            )

    @staticmethod
    def get_field_name(document):
        """
        Возвращает имя поля формы для документа.
        """
        return f"accept_{document.document_type}"

    def clean(self):
        """
        Требует явного принятия каждого документа.
        """
        cleaned_data = super().clean()

        for document in self.documents:
            field_name = self.get_field_name(document)

            if not cleaned_data.get(field_name):
                self.add_error(
                    field_name,
                    _(
                        "Для продолжения необходимо принять этот документ."
                    ),
                )

        return cleaned_data