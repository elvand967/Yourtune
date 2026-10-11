
# apps/core/admin/__init__.py
#============================

from .seo import (
    SEOReplacementAdmin,
    StopWordAdmin,
)
from .cookie_consent import CookieConsentAdmin

__all__ = [
    "SEOReplacementAdmin",
    "StopWordAdmin",
    "CookieConsentAdmin",
]