# apps/users/urls.py
# ===================

from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from apps.users import views


app_name = "users"


urlpatterns = [
    # =========================================================
    # Аутентификация
    # =========================================================

    path(
        "login/",
        views.UnifiedLoginView.as_view(),
        name="login",
    ),

    path(
        "login/email/",
        views.CustomLoginView.as_view(),
        name="email_login",
    ),

    path(
        "signup/",
        views.CustomSignupView.as_view(),
        name="signup",
    ),

    path(
        "logout/",
        views.CustomLogoutView.as_view(),
        name="logout",
    ),

    # =========================================================
    # Allauth
    # =========================================================

    path(
        "accounts/",
        include("allauth.urls"),
    ),

    # =========================================================
    # Восстановление пароля
    # =========================================================

    path(
        "password/reset/",
        TemplateView.as_view(
            template_name="users/auth/password_reset.html",
        ),
        name="password_reset",
    ),

    path(
        "password/reset/done/",
        TemplateView.as_view(
            template_name="users/auth/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    # =========================================================
    # Профиль
    # =========================================================

    path(
        "profile/",
        views.ProfileDetailView.as_view(),
        name="profile_detail",
    ),

    path(
        "profile/edit/",
        views.ProfileUpdateView.as_view(),
        name="profile_edit",
    ),

    path(
        "profile/upload-avatar/",
        views.UploadAvatarView.as_view(),
        name="upload_avatar",
    ),

    path(
        "profile/reset-avatar/",
        views.ResetAvatarView.as_view(),
        name="reset_avatar",
    ),

    # =========================================================
    # Плейлисты и избранное
    # =========================================================

    path(
        "playlists/",
        views.PlaylistListView.as_view(),
        name="playlists_list",
    ),

    path(
        "favorites/",
        views.FavoritesView.as_view(),
        name="favorites",
    ),

    # =========================================================
    # Безопасность
    # =========================================================

    path(
        "security/password/change/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),

    path(
        "security/sessions/",
        views.SessionsView.as_view(),
        name="sessions",
    ),

    path(
        "security/two-factor/",
        views.TwoFactorView.as_view(),
        name="two_factor",
    ),

    # =========================================================
    # Настройки
    # =========================================================

    path(
        "settings/",
        views.SettingsView.as_view(),
        name="settings",
    ),

    path(
        "settings/account/",
        views.AccountSettingsView.as_view(),
        name="account_settings",
    ),

    path(
        "settings/privacy/",
        views.PrivacySettingsView.as_view(),
        name="privacy",
    ),

    path(
        "settings/notifications/",
        views.NotificationsView.as_view(),
        name="notifications",
    ),

    # =========================================================
    # Интеграции
    # =========================================================

    path(
        "integrations/",
        views.IntegrationsView.as_view(),
        name="integrations",
    ),

    path(
        "integrations/api-tokens/",
        views.ApiTokensView.as_view(),
        name="api_tokens",
    ),

    path(
        "integrations/social-accounts/",
        views.SocialAccountsView.as_view(),
        name="social_accounts",
    ),

    # =========================================================
    # Администрирование пользователей
    # =========================================================

    path(
        "admin/users/",
        views.AdminUserListView.as_view(),
        name="admin_user_list",
    ),

    path(
        "admin/users/<uuid:pk>/",
        views.AdminUserDetailView.as_view(),
        name="admin_user_detail",
    ),

    path(
        "admin/users/<uuid:pk>/edit/",
        views.AdminUserUpdateView.as_view(),
        name="admin_user_edit",
    ),

    # =========================================================
    # Администрирование ролей
    # =========================================================

    path(
        "admin/roles/",
        views.AdminRoleListView.as_view(),
        name="admin_role_list",
    ),

    path(
        "admin/roles/create/",
        views.AdminRoleCreateView.as_view(),
        name="admin_role_create",
    ),

    path(
        "admin/roles/<uuid:pk>/edit/",
        views.AdminRoleUpdateView.as_view(),
        name="admin_role_update",
    ),

    path(
        "admin/roles/<uuid:pk>/delete/",
        views.AdminRoleDeleteView.as_view(),
        name="admin_role_delete",
    ),

    # =========================================================
    # Аудит
    # =========================================================

    path(
        "admin/audit/",
        views.AdminAuditLogView.as_view(),
        name="admin_audit_log",
    ),

    path(
        "admin/audit/<uuid:pk>/",
        views.AdminAuditLogDetailView.as_view(),
        name="admin_audit_detail",
    ),
]