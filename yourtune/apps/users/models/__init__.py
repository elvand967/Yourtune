
# apps/users/models/__init__.py
"""
Модели приложения users.
"""


from apps.users.models.custom_user import CustomUser  # noqa
from apps.users.models.profile import Profile  # noqa
from apps.users.models.social_account import SocialAccount  # noqa

# Заглушки для будущих моделей
from .playlist import Playlist
from .favorite import Favorite

from apps.users.models.role import Role, UserRole  # noqa
from apps.users.models.audit_log import AuditLog  # noqa

__all__ = [
    'CustomUser',
    'Profile',
    'SocialAccount',
    'Playlist',
    'Favorite',
    'Role',
    'UserRole',
    'AuditLog',
]