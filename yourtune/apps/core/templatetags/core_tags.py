# apps/core/templatetags/core_tags.py
# Templatetags для главного меню YourTune

from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.inclusion_tag('core/includes/main_menu.html', takes_context=True)
def main_menu(context):
    """
    Тег генерации главного меню для YourTune.

    Возвращает список пунктов меню для шаблона.
    """
    request = context.get('request')
    user = request.user if request else None

    # Базовое публичное меню
    menu_items = [
        {
            'title': 'Главная',
            'url': 'main:home',
            'url_name': 'main:home',
            'icon': '🏠',
            'children': []
        },
        {
            'title': 'О проекте',
            'url': 'main:about',
            'url_name': 'main:about',
            'icon': 'ℹ️',
            'children': [
                {
                    'title': 'Политика',
                    'url': 'account_login',
                    'url_name': 'account_login',
                    'icon': '🔑'
                },
                {
                    'title': 'Правила',
                    'url': 'account_signup',
                    'url_name': 'account_signup',
                    'icon': '📝'
                }
            ]
        },
        {
            'title': 'FAQ',
            'url': 'main:faq',
            'url_name': 'main:faq',
            'icon': '❓',
            'children': []
        },
        {
            'title': 'Блог',
            'url': 'main:blog',
            'url_name': 'main:blog',
            'icon': '📝',
            'children': []
        },
    ]

    # Проверка авторизации
    is_authenticated = user and user.is_authenticated

    # Проверка на суперпользователя
    is_superuser = user and user.is_superuser

    if is_authenticated:
        # Админ-панель для суперпользователей
        admin_url = None
        if is_superuser:
            try:
                admin_url = reverse('admin:index')
            except NoReverseMatch:
                admin_url = '/admin/'

        # Профиль пользователя
        profile_menu = {
            'title': user.first_name or user.username or 'Профиль',
            'url': 'users:profile_edit',
            'url_name': 'users:profile_edit',
            'icon': '👤',
            'is_profile': True,
            'children': []
        }

        # Добавляем админ-панель первой ссылкой для суперпользователей
        if admin_url:
            profile_menu['children'].append({
                'title': 'Админ-панель',
                'url': admin_url,
                'icon': '🛠️',
                'is_admin': True
            })

        # Остальные пункты профиля
        profile_menu['children'].extend([
            {
                'title': 'Мой профиль',
                'url': 'users:profile_edit',
                'url_name': 'users:profile_edit',
                'icon': '⚙️'
            },
            {
                'title': 'Избранное',
                'url': 'users:favorites',
                'url_name': 'users:favorites',
                'icon': '⭐'
            },
            {
                'title': 'Настройки',
                'url': 'users:settings',
                'url_name': 'users:settings',
                'icon': '🔧'
            },
            {
                'title': 'Выйти',
                'url': 'account_logout',
                'url_name': 'account_logout',
                'icon': '🚪'
            }
        ])
    else:
        # Меню для гостей (вход/регистрация)
        profile_menu = {
            'title': 'Войти',
            'url': 'account_login',
            'url_name': 'account_login',
            'icon': '🔑',
            'is_auth': True,
            'children': [
                {
                    'title': 'Войти',
                    'url': 'account_login',
                    'url_name': 'account_login',
                    'icon': '🔑'
                },
                {
                    'title': 'Регистрация',
                    'url': 'account_signup',
                    'url_name': 'account_signup',
                    'icon': '📝'
                }
            ]
        }

    # Валидация URL (проверка на существование)
    validated_menu = []
    for item in menu_items:
        try:
            reverse(item['url_name'])
            validated_menu.append(item)
        except NoReverseMatch:
            # Если URL не найден, пропускаем пункт меню
            continue

    return {
        'menu_items': validated_menu,
        'profile_menu': profile_menu,
        'is_authenticated': is_authenticated,
        'is_superuser': is_superuser,
        'request': request,
    }