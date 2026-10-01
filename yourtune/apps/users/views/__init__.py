# apps/users/views/__init__.py
# ===========================

from apps.users.views.auth import (
    CustomLoginView,
    CustomLogoutView,
    CustomSignupView,
    CustomSocialSignupView,
    UnifiedLoginView,
)

from apps.users.views.integrations import (
    ApiTokensView,
    IntegrationsView,
    SocialAccountsView,
)

from apps.users.views.playlists import (
    FavoritesView,
    PlaylistListView,
)

from apps.users.views.profile import (
    ProfileDetailView,
    ProfileUpdateView,
    ResetAvatarView,
    UploadAvatarView,
)

from apps.users.views.security import (
    PasswordChangeView,
    SessionsView,
    TwoFactorView,
)

from apps.users.views.settings import (
    AccountSettingsView,
    NotificationsView,
    PrivacySettingsView,
    SettingsView,
)

from apps.users.views.admin.audit import (
    AdminAuditLogDetailView,
    AdminAuditLogView,
)

from apps.users.views.admin.roles import (
    AdminRoleCreateView,
    AdminRoleDeleteView,
    AdminRoleListView,
    AdminRoleUpdateView,
)

from apps.users.views.admin.users import (
    AdminUserDetailView,
    AdminUserListView,
    AdminUserUpdateView,
)


__all__ = [
    # Аутентификация
    "UnifiedLoginView",
    "CustomLoginView",
    "CustomSignupView",
    "CustomLogoutView",
    "CustomSocialSignupView",

    # Профиль
    "ProfileDetailView",
    "ProfileUpdateView",
    "UploadAvatarView",
    "ResetAvatarView",

    # Плейлисты
    "PlaylistListView",
    "FavoritesView",

    # Безопасность
    "PasswordChangeView",
    "SessionsView",
    "TwoFactorView",

    # Настройки
    "SettingsView",
    "AccountSettingsView",
    "PrivacySettingsView",
    "NotificationsView",

    # Интеграции
    "IntegrationsView",
    "ApiTokensView",
    "SocialAccountsView",

    # Администрирование пользователей
    "AdminUserListView",
    "AdminUserDetailView",
    "AdminUserUpdateView",

    # Администрирование ролей
    "AdminRoleListView",
    "AdminRoleCreateView",
    "AdminRoleUpdateView",
    "AdminRoleDeleteView",

    # Аудит
    "AdminAuditLogView",
    "AdminAuditLogDetailView",
]