# apps/core/templatetags/main_menu.py
# ===================================

from django import template
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from apps.legal.models import LegalDocument

register = template.Library()

User = get_user_model()


@register.inclusion_tag(
    "core/includes/main_menu.html",
    takes_context=True,
)
def main_menu(context):
    """
    Тег генерации главного меню для YourTune.

    Возвращает:
    - menu_items — основное публичное меню;
    - profile_menu — меню пользователя.
    """
    request = context.get("request")
    user = request.user if request else None

    active_documents = (
        LegalDocument.objects
        .filter(is_active=True)
        .order_by("menu_order")
    )

    document_children = [
        {
            "title": (
                    document.menu_title
                    or document.title
            ),
            "url": document.get_absolute_url(),
            "url_name": None,
            "icon": "📄",
        }
        for document in active_documents
    ]

    menu_items = [
        {
            "title": "Главная",
            "url_name": "main:home",
            "icon": "🏠",
            "children": [],
        },
        {
            "title": "О проекте",
            "url_name": "main:about",
            "icon": "ℹ️",
            "children": [
                {
                    "title": "О нас",
                    "url_name": "main:about",
                    "icon": "ℹ️",
                },
                {
                    "title": "Документы",
                    "url_name": "legal:document_list",
                    "icon": "📄",
                    "children": document_children,
                },
            ],
        },
        {
            "title": "FAQ",
            "url_name": "main:faq",
            "icon": "❓",
            "children": [],
        },
        {
            "title": "Блог",
            "url_name": "main:blog",
            "icon": "📝",
            "children": [],
        },
    ]

    is_authenticated = user and user.is_authenticated
    is_superuser = user and user.is_superuser

    if is_authenticated:
        admin_url = None

        if is_superuser:
            try:
                admin_url = reverse("admin:index")
            except NoReverseMatch:
                admin_url = "/admin/"

        profile_menu = {
            "title": (
                user.get_full_name()
                or user.email
                or "Профиль"
            ),
            "url_name": "users:profile_edit",
            "icon": "👤",
            "children": [],
        }

        if admin_url:
            profile_menu["children"].append(
                {
                    "title": "Админ-панель",
                    "url": admin_url,
                    "url_name": None,
                    "icon": "🛠️",
                    "is_admin": True,
                }
            )

        profile_menu["children"].extend(
            [
                {
                    "title": "Личный кабинет",
                    "url_name": "users:profile_detail",
                    "icon": "⚙️",
                },
                {
                    "title": "Плейлисты",
                    "url_name": "users:playlists_list",
                    "icon": "🎵",
                },
                {
                    "title": "Избранное",
                    "url_name": "users:favorites",
                    "icon": "⭐",
                },
                {
                    "title": "Настройки",
                    "url_name": "users:settings",
                    "icon": "🔧",
                },
                {
                    "title": "Выйти",
                    "url_name": "account_logout",
                    "icon": "🚪",
                },
            ]
        )
    else:
        profile_menu = {
            "title": "Войти",
            "url_name": "account_login",
            "icon": "🔑",
            "children": [
                {
                    "title": "Авторизация",
                    "url_name": "users:login",
                    "icon": "🔑",
                },
                {
                    "title": "Регистрация",
                    "url_name": "users:signup",
                    "icon": "📝",
                },
            ],
        }

    validated_menu = []

    for item in menu_items:
        if not _is_valid_url(item):
            continue

        item["children"] = _validate_children(
            item.get("children", []),
        )

        validated_menu.append(item)

    profile_menu["children"] = _validate_children(
        profile_menu.get("children", []),
    )

    return {
        "menu_items": validated_menu,
        "profile_menu": profile_menu,
    }


def _is_valid_url(item):
    """
    Проверяет, что URL пункта меню существует.
    """
    if item.get("is_admin"):
        return True

    url_name = item.get("url_name")

    if not url_name:
        return bool(item.get("url"))

    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False


def _validate_children(children):
    """
    Удаляет пункты подменю с несуществующими URL.
    """
    validated_children = []

    for child in children:
        if not _is_valid_url(child):
            continue

        child["children"] = _validate_children(
            child.get("children", []),
        )

        validated_children.append(child)

    return validated_children