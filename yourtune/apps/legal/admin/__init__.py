# apps/legal/admin/__init__.py

from apps.legal.admin.documents import (
    LegalDocumentAdmin,
    LegalDocumentVersionAdmin,
)
from apps.legal.admin.consents import UserLegalConsentAdmin

__all__ = [
    "LegalDocumentAdmin",
    "LegalDocumentVersionAdmin",
    "UserLegalConsentAdmin",
]