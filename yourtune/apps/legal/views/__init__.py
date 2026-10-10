
# apps/legal/views/__init__.py

from apps.legal.views.documents import (
    LegalDocumentDetailView,
    PolicyDetailView,
    TermsDetailView,
)
from apps.legal.views.consent import RequiredConsentView

__all__ = [
    "LegalDocumentDetailView",
    "PolicyDetailView",
    "TermsDetailView",
    "RequiredConsentView",
]