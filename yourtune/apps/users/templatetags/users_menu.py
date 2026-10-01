# apps/users/templatetags/users_menu.py
# =====================================

from django import template
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()


@register.simple_tag(takes_context=True)
def users_menu(context):
    """
    Тег генерации меню личного кабинета.
    Возвращает:
      - header_menu_items: основное меню ЛК
      - header_profile_menu: выпадающее меню профиля
    """
    request = context.get('request')
    user = request.user if request else None

    is_authenticated = user and user.is_authenticated

    if not is_authenticated:
        return {
            'header_menu_items': [],
            'header_profile_menu': None,
        }

    # ---------------------------------------------------------
    # Основное меню ЛК
    # ---------------------------------------------------------
    header_menu_items = [
        {
            'title': 'Главная',
            'url_name': 'main:home',
            'icon': '🏠',
            'children': []
        },
        {
            'title': 'Профиль',
            'url_name': 'users:profile_detail',
            'icon': '👤',
            'children': []
        },
        {
            'title': 'Плейлисты',
            'url_name': 'users:playlists_list',
            'icon': '🎵',
            'children': [
                {'title': 'Мои плейлисты', 'url_name': 'users:playlists_list', 'icon': '🎵'},
                {'title': 'Избранное', 'url_name': 'users:favorites', 'icon': '⭐'},
            ]
        },
        {
            'title': 'Безопасность',
            'url_name': 'users:security',
            'icon': '🔒',
            'children': [
                {'title': 'Смена пароля', 'url_name': 'users:password_change', 'icon': '🔑'},
                {'title': 'Сессии', 'url_name': 'users:sessions', 'icon': '💻'},
                {'title': '2FA', 'url_name': 'users:two_factor', 'icon': '📱'},
            ]
        },
        {
            'title': 'Настройки',
            'url_name': 'users:settings',
            'icon': '🔧',
            'children': [
                {'title': 'Аккаунт', 'url_name': 'users:account_settings', 'icon': '⚙️'},
                {'title': 'Приватность', 'url_name': 'users:privacy', 'icon': '🛡️'},
                {'title': 'Уведомления', 'url_name': 'users:notifications', 'icon': '🔔'},
            ]
        },
        {
            'title': 'Интеграции',
            'url_name': 'users:integrations',
            'icon': '🔗',
            'children': [
                {'title': 'API токены', 'url_name': 'users:api_tokens', 'icon': '🔐'},
                {'title': 'Соц. аккаунты', 'url_name': 'users:social_accounts', 'icon': '🌐'},
            ]
        },
    ]

    # ---------------------------------------------------------
    # Выпадающее меню профиля (справа в хедере)
    # ---------------------------------------------------------
    profile_menu = {
        'title': user.get_full_name() or user.email or 'Профиль',
        'url_name': 'users:profile_detail',
        'icon': '👤',
        'children': [
            {'title': 'Мой профиль', 'url_name': 'users:profile_detail', 'icon': '👤'},
            {'title': 'Настройки', 'url_name': 'users:settings', 'icon': '🔧'},
            {'title': 'Безопасность', 'url_name': 'users:security', 'icon': '🔒'},
            {'title': 'Выйти', 'url_name': 'account_logout', 'icon': '🚪'},
        ]
    }

    # ---------------------------------------------------------
    # Админ-раздел для суперпользователей и стаффа
    # ---------------------------------------------------------
    if user.is_superuser or user.is_staff:
        try:
            admin_url = reverse('admin:index')
        except NoReverseMatch:
            admin_url = '/admin/'

        # Добавляем в основное меню
        header_menu_items.append({
            'title': 'Админ-панель',
            'url': admin_url,
            'url_name': None,
            'icon': '🛠️',
            'is_admin': True,
            'children': []
        })

        # Добавляем в профильное меню
        profile_menu['children'].insert(0, {
            'title': 'Админ-панель',
            'url': admin_url,
            'url_name': None,
            'icon': '🛠️',
            'is_admin': True
        })

        # Расширенное админ-меню для суперпользователей
        if user.is_superuser:
            admin_children = [
                {'title': 'Пользователи', 'url_name': 'users:admin_user_list', 'icon': '👥'},
                {'title': 'Роли', 'url_name': 'users:admin_role_list', 'icon': '🎭'},
                {'title': 'Группы', 'url_name': 'admin:auth_group_changelist', 'icon': '👪'},
                {'title': 'Аудит', 'url_name': 'users:admin_audit_log', 'icon': '📋'},
            ]
            # Находим последний admin-элемент и добавляем children
            for item in reversed(header_menu_items):
                if item.get('is_admin'):
                    item['children'] = admin_children
                    break

    # ---------------------------------------------------------
    # Валидация URL (основное меню)
    # ---------------------------------------------------------
    validated_menu = []
    for item in header_menu_items:
        if item.get('is_admin'):
            # Админ-ссылки не валидируем через reverse
            validated_menu.append(item)
        else:
            try:
                reverse(item['url_name'])
                validated_menu.append(item)
            except NoReverseMatch:
                continue

        # Валидация children
        validated_children = []
        for child in item.get('children', []):
            if child.get('is_admin'):
                validated_children.append(child)
            else:
                try:
                    reverse(child['url_name'])
                    validated_children.append(child)
                except NoReverseMatch:
                    continue
        item['children'] = validated_children

    # ---------------------------------------------------------
    # Валидация URL (профильное меню)
    # ---------------------------------------------------------
    validated_profile_children = []
    for child in profile_menu.get('children', []):
        if child.get('is_admin'):
            validated_profile_children.append(child)
        else:
            try:
                reverse(child['url_name'])
                validated_profile_children.append(child)
            except NoReverseMatch:
                continue

    profile_menu['children'] = validated_profile_children

    return {
        'header_menu_items': validated_menu,
        'header_profile_menu': profile_menu,
    }