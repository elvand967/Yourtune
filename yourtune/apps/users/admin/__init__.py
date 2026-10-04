
# apps/users/admin/__init__.py

from .custom_user import CustomUserAdmin
from .profile import ProfileAdmin

__all__ = ("CustomUserAdmin", "ProfileAdmin")