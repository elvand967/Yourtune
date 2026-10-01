# apps/users/views/admin/__init__.py
# =====================================

from apps.users.views.admin.users import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserUpdateView,
)
from apps.users.views.admin.roles import (
    AdminRoleListView,
    AdminRoleCreateView,
    AdminRoleUpdateView,
    AdminRoleDeleteView,
)
from apps.users.views.admin.audit import (
    AdminAuditLogView,
    AdminAuditLogDetailView,
)

__all__ = [
    # Users
    'AdminUserListView',
    'AdminUserDetailView',
    'AdminUserUpdateView',
    # Roles
    'AdminRoleListView',
    'AdminRoleCreateView',
    'AdminRoleUpdateView',
    'AdminRoleDeleteView',
    # Audit
    'AdminAuditLogView',
    'AdminAuditLogDetailView',
]