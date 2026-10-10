# apps/legal/models/__init__.py

from apps.legal.models.documents import LegalDocument, LegalDocumentVersion
from apps.legal.models.consents import UserLegalConsent

__all__ = [
    "LegalDocument",
    "LegalDocumentVersion",
    "UserLegalConsent",
]