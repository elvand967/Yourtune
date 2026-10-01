# apps/core/templatetags/main_menu.py
# ===================================

from django import template
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()


@register.inclusion_tag('core/includes/main_menu.html', takes_context=True)
def main_menu(context):
    """
    Тег генерации главного меню для YourTune.
    Возвращает menu_items и profile_menu.
    """
    request = context.get('request')
    user = request.user if request else None

    # Базовое публичное меню
    menu_items = [
        {
            'title': 'Главная',
            'url_name': 'main:home',
            'icon': '🏠',
            'children': []
        },
        {
            'title': 'О проекте',
            'url_name': 'main:about',
            'icon': 'ℹ️',
            'children': [
                {'title': 'О нас', 'url_name': 'main:about', 'icon': 'ℹ️'},
                {'title': 'Политика', 'url_name': 'main:policy', 'icon': '🛡️'},
                {'title': 'Правила', 'url_name': 'main:rules', 'icon': '📜'},
            ]
        },
        {
            'title': 'FAQ',
            'url_name': 'main:faq',
            'icon': '❓',
            'children': []
        },
        {
            'title': 'Блог',
            'url_name': 'main:blog',
            'icon': '📝',
            'children': []
        },
    ]

    is_authenticated = user and user.is_authenticated
    is_superuser = user and user.is_superuser

    if is_authenticated:
        admin_url = None
        if is_superuser:
            try:
                admin_url = reverse('admin:index')
            except NoReverseMatch:
                admin_url = '/admin/'

        profile_menu = {
            'title': user.get_full_name() or user.email or 'Профиль',
            'url_name': 'users:profile_edit',
            'icon': '👤',
            'children': []
        }

        if admin_url:
            profile_menu['children'].append({
                'title': 'Админ-панель',
                'url': admin_url,
                'url_name': None,
                'icon': '🛠️',
                'is_admin': True
            })

        profile_menu['children'].extend([
            {'title': 'Личный кабинет', 'url_name': 'users:profile_detail', 'icon': '⚙️'},
            {'title': 'Плейлисты', 'url_name': 'users:playlists_list', 'icon': '🎵'},
            {'title': 'Избранное', 'url_name': 'users:favorites', 'icon': '⭐'},
            {'title': 'Настройки', 'url_name': 'users:settings', 'icon': '🔧'},
            {'title': 'Выйти', 'url_name': 'account_logout', 'icon': '🚪'},
        ])
    else:
        profile_menu = {
            'title': 'Войти',
            'url_name': 'account_login',
            'icon': '🔑',
            'children': [
                {'title': 'Авторизация', 'url_name': 'users:login', 'icon': '🔑'},
                {'title': 'Регистрация', 'url_name': 'users:signup', 'icon': '📝'},
            ]
        }

    # Валидация URL
    validated_menu = []
    for item in menu_items:
        try:
            reverse(item['url_name'])
            validated_menu.append(item)
        except NoReverseMatch:
            continue

    # Валидация children
    validated_children = []
    for child in profile_menu.get('children', []):
        if child.get('is_admin'):
            validated_children.append(child)
        else:
            try:
                reverse(child['url_name'])
                validated_children.append(child)
            except NoReverseMatch:
                continue

    profile_menu['children'] = validated_children

    return {
        'menu_items': validated_menu,
        'profile_menu': profile_menu,
    }