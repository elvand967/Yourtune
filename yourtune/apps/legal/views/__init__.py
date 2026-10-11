
# apps/legal/views/__init__.py

"""
Пакет views приложения legal.

Публичные view-классы импортируются здесь,
чтобы использовать понятные импорты в urls.py:

from apps.legal import views

views.LegalDocumentListView.as_view()
views.LegalDocumentDetailView.as_view()
views.RequiredConsentView.as_view()
"""

from .consent import RequiredConsentView
from .documents import (
    LegalDocumentDetailView,
    LegalDocumentListView,
)

__all__ = (
    "RequiredConsentView",
    "LegalDocumentDetailView",
    "LegalDocumentListView",
)