# apps/legal/admin/__init__.py
# ==============================

from .consents import UserLegalConsentAdmin
from .documents import (
    LegalDocumentAdmin,
    LegalDocumentVersionAdmin,
)

__all__ = [
    "LegalDocumentAdmin",
    "LegalDocumentVersionAdmin",
    "UserLegalConsentAdmin",
]