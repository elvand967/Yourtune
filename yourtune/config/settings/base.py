
# =========================================================
# yourtune/config/settings/base.py
# =========================================================
# Базовые настройки Django-проекта YourTune
# Версия django-allauth: 65.19.2
# =========================================================


# =========================================================
# ИМПОРТЫ И БАЗОВЫЕ ПУТИ
# =========================================================

import os
from dotenv import load_dotenv
from pathlib import Path

# BASE_DIR — корневая директория проекта (на 3 уровня выше этого файла)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =========================================================
# ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (.env файл)
# =========================================================
# load_dotenv() загружает переменные из файла .env в окружение процесса
# Вызывается ОДИН раз в начале файла
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
# Секретный ключ для криптографической подписи (сессии, токены, CSRF)
# Хранится в .env, не коммитить в репозиторий!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG=True показывает детальные ошибки (не включать на продакшене!)
# Строка 'True' из .env преобразуется в булево значение
DEBUG = os.getenv('DEBUG') == 'True'

# =========================================================
# КАСТОМНАЯ МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
# =========================================================
# Указываем ДО создания миграций, чтобы Django использовал CustomUser
# вместо встроенной auth.User
# Модель должна наследоваться от AbstractBaseUser + PermissionsMixin
AUTH_USER_MODEL = "users.CustomUser"

# =========================================================
# УСТАНОВЛЕННЫЕ ПРИЛОЖЕНИЯ (INSTALLED_APPS)
# =========================================================
# Порядок важен: сначала django.contrib, потом allauth, потом кастомные apps
INSTALLED_APPS = [
    # Стандартные приложения Django
    "django.contrib.admin",  # Админ-панель
    "django.contrib.auth",  # Система аутентификации
    "django.contrib.contenttypes",  # Система типов контента
    "django.contrib.sessions",  # Сессии пользователей
    "django.contrib.messages",  # Система сообщений
    "django.contrib.staticfiles",  # Статические файлы (CSS, JS, изображения)
    "django.contrib.sites",  # Мульти-сайт (требуется для allauth)

    "django_ckeditor_5",

    # =========================================================
    # ALLAUTH (аутентификация через email и соц. сети)
    # =========================================================
    "allauth",  # Ядро allauth
    "allauth.account",  # Email-аутентификация (регистрация, вход)
    "allauth.socialaccount",  # Социальная аутентификация (OAuth2)
    "allauth.socialaccount.providers.google",  # Google OAuth2 (встроенный провайдер)

    # =========================================================
    # ✅ ПОДКЛЮЧАЕМ ВСТРОЕННЫЙ ПРОВАЙДЕР ЯНДЕКСА
    # =========================================================
    "allauth.socialaccount.providers.yandex",  # Вместо "apps.users.providers.yandex"

    # =========================================================
    # КАСТОМНЫЕ ПРИЛОЖЕНИЯ ПРОЕКТА
    # =========================================================
    "apps.core.apps.CoreConfig",    # Общие утилиты, контекст-процессоры
    "apps.users.apps.UsersConfig",  # Пользователи, профили, адаптеры, формы
    'apps.main.apps.MainConfig',    # Главная страница, статические разделы
    'apps.legal.apps.LegalConfig',  # Юридические документы
    'apps.notifications.apps.NotificationsConfig',  # Уведомления
]

# =========================================================
# CREDENTIALS OAUTH2 (ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ)
# =========================================================
# ОБЯЗАТЕЛЬНО объявлять ПЕРЕД SOCIALACCOUNT_PROVIDERS,
# иначе будет NameError при загрузке настроек
#
# Эти переменные читаются из .env файла:
#   SOCIALACCOUNT_GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
#   SOCIALACCOUNT_GOOGLE_SECRET=GOCSPX-xxxxx
#   SOCIALACCOUNT_YANDEX_CLIENT_ID=xxxxx
#   SOCIALACCOUNT_YANDEX_SECRET=xxxxx

SOCIALACCOUNT_GOOGLE_CLIENT_ID = os.getenv('SOCIALACCOUNT_GOOGLE_CLIENT_ID', '')
SOCIALACCOUNT_GOOGLE_SECRET = os.getenv('SOCIALACCOUNT_GOOGLE_SECRET', '')

SOCIALACCOUNT_YANDEX_CLIENT_ID = os.getenv('SOCIALACCOUNT_YANDEX_CLIENT_ID', '')
SOCIALACCOUNT_YANDEX_SECRET = os.getenv('SOCIALACCOUNT_YANDEX_SECRET', '')

# =========================================================
# ALLAUTH: БАЗОВЫЕ НАСТРОЙКИ
# =========================================================
# Версия django-allauth: 65.19.2
# Документация: https://docs.allauth.org/

# SITE_ID — идентификатор текущего сайта (требуется для django.contrib.sites)
# Все SocialApp в админке должны быть привязаны к этому сайту (или к "всем")
SITE_ID = 1

# =========================================================
# БЭКЕНДЫ АУТЕНТИФИКАЦИИ
# =========================================================
# Порядок важен: сначала ModelBackend (для админки), потом allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Стандартная аутентификация Django
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth (email + соц. сети)
]

# =========================================================
# ALLAUTH ACCOUNT (EMAIL-АУТЕНТИФИКАЦИЯ)
# =========================================================
# Настройки для встроенной системы регистрации/входа по email

# Методы входа: только email (username отключён)
ACCOUNT_LOGIN_METHODS = {'email'}

# Поля, обязательные при регистрации: email + два пароля
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

# Подтверждение email: 'optional' (не обязательно), 'mandatory' (обязательно), 'none' (отключено)
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# Автоматический вход после подтверждения email
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Выход по GET-запросу (удобно для кнопки "Выйти" в меню)
ACCOUNT_LOGOUT_ON_GET = True

# Запоминать сессию после закрытия браузера
ACCOUNT_SESSION_REMEMBER = True

# =========================================================
# ОТКЛЮЧЕНИЕ USERNAME
# =========================================================
# Используем email как уникальный идентификатор вместо username

# Поле username в модели пользователя не используется
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# =========================================================
# ALLAUTH SOCIALACCOUNT (СОЦИАЛЬНАЯ АУТЕНТИФИКАЦИЯ)
# =========================================================
# Настройки для входа через Google, Yandex и других OAuth2-провайдеров

# Автоматическая регистрация новых пользователей без дополнительной формы
# SOCIALACCOUNT_AUTO_SIGNUP = True

# Google/Yandex не создают аккаунт автоматически:
# новый пользователь попадёт на страницу завершения регистрации, где должен явно принять документы согласия.
SOCIALACCOUNT_AUTO_SIGNUP = False

# Email обязателен для социальных аккаунтов
SOCIALACCOUNT_EMAIL_REQUIRED = True

# Запрашивать email у провайдера во время OAuth2-flow
SOCIALACCOUNT_QUERY_EMAIL = True

# Подтверждение email для соц. аккаунтов: 'optional' (не обязательно)
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'


# =========================================================
# АДАПТЕРЫ ALLAUTH
# =========================================================

# Адаптер для email-аутентификации (вход, регистрация, сброс пароля)
ACCOUNT_ADAPTER = 'apps.users.adapters.CustomAccountAdapter'

# Адаптер для соц. аутентификации (Google, Yandex)
SOCIALACCOUNT_ADAPTER = 'apps.users.adapters.CustomSocialAccountAdapter'

# Отключение промежуточной страницы (bridge page) после OAuth2-редиректа
# Если True — сразу перенаправляет на LOGIN_REDIRECT_URL после успеха
SOCIALACCOUNT_LOGIN_ON_REDIRECT = True

# =========================================================
# ФОРМЫ ALLAUTH
# =========================================================

ACCOUNT_FORMS = {
    'login': 'apps.users.forms.auth.CustomLoginForm',
    'signup': 'apps.users.forms.auth.CustomSignupForm',
    'reset_password': 'apps.users.forms.auth.CustomResetPasswordForm',  # ✅ Добавлено
}

SOCIALACCOUNT_FORMS = {
    'signup': 'apps.users.forms.auth.CustomSocialSignupForm',
}

# =========================================================
# НАСТРОЙКИ OAUTH2-ПРОВАЙДЕРОВ
# =========================================================
# В allauth 65.x ОБЯЗАТЕЛЬНО указывать 'APP' с client_id и secret,
# иначе будет ошибка SocialApp.DoesNotExist или промежуточная форма

SOCIALACCOUNT_PROVIDERS = {
    # ---------------------------------------------------------
    # GOOGLE OAUTH2
    # ---------------------------------------------------------
    'google': {
        # Запрашиваемые разрешения (scope): профиль + email
        'SCOPE': ['profile', 'email'],

        # Параметры авторизации: access_type='online' для одностраничного входа
        'AUTH_PARAMS': {'access_type': 'online'},

        # PKCE (Proof Key for Code Exchange) — защита от CSRF в OAuth2
        'OAUTH_PKCE_ENABLED': True,

        # Считать email подтверждённым (Google верифицирует email сам)
        'VERIFIED_EMAIL': True,

        # =========================================================
        # CREDENTIALS (ОБЯЗАТЕЛЬНО для allauth 65.x!)
        # =========================================================
        # Без этого блока allauth не сможет построить OAuth2-ссылку
        # и покажет промежуточную форму "Вход через Google"
        'APP': {
            'client_id': SOCIALACCOUNT_GOOGLE_CLIENT_ID,  # Из .env
            'secret': SOCIALACCOUNT_GOOGLE_SECRET,  # Из .env
        },
    },

    # ---------------------------------------------------------
    # YANDEX OAUTH2
    # ---------------------------------------------------------
    'yandex': {
        # Права доступа к данным Yandex ID.
        # В кабинете приложения Yandex OAuth также должны быть
        # активированы соответствующие разрешения.
        'SCOPE': [
            'login:email',
            'login:info',
        ],

        # Не задаём scope вручную и не передаём недокументированный language.
        'AUTH_PARAMS': {},

        'APP': {
            'client_id': SOCIALACCOUNT_YANDEX_CLIENT_ID,
            'secret': SOCIALACCOUNT_YANDEX_SECRET,
        },
    },
}

# =========================================================
# URL REDIRECTS (ПЕРЕНАПРАВЛЕНИЯ ПОСЛЕ ВХОДА/ВЫХОДА)
# =========================================================
# Эти URL используются allauth и @login_required декоратором

LOGIN_URL = 'users:login'  # Куда перенаправлять неавторизованных (название URL из users/urls.py)
LOGIN_REDIRECT_URL = 'users:profile_detail'  # Куда после успешного входа
LOGOUT_REDIRECT_URL = 'main:home'  # Куда после выхода

# =========================================================
# MIDDLEWARE (ОБРАБОТЧИКИ ЗАПРОСОВ)
# =========================================================
# Порядок важен! AccountMiddleware должен быть после AuthenticationMiddleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Безопасность (HTTPS, HSTS)
    "django.contrib.sessions.middleware.SessionMiddleware",  # Сессии
    "django.middleware.common.CommonMiddleware",  # Общие утилиты (APPEND_SLASH и т.д.)
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF-защита
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Аутентификация (request.user)
    "allauth.account.middleware.AccountMiddleware",  # Allauth (соц. аккаунты, messages)
    "django.contrib.messages.middleware.MessageMiddleware",  # Система сообщений
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Защита от clickjacking
]

# =========================================================
# ROOT URLCONF (ГЛАВНЫЙ MARSHRUTIZATOR)
# =========================================================
# Указывает на файл с URL-маршрутами проекта
ROOT_URLCONF = "config.urls"

# =========================================================
# TEMPLATES (НАСТРОЙКИ ШАБЛОНОВ)
# =========================================================
TEMPLATES = [
    {
        # Бэкенд для обработки Django-шаблонов
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Дополнительные директории с шаблонами (кроме app-директорий)
        "DIRS": [BASE_DIR / "templates"],

        # APP_DIRS=True автоматически ищет шаблоны в папке templates/ каждого приложения
        "APP_DIRS": True,

        # Контекст-процессоры (переменные, доступные во всех шаблонах)
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",  # request в шаблонах
                "django.contrib.auth.context_processors.auth",  # user, perms в шаблонах
                "django.contrib.messages.context_processors.messages",  # messages в шаблонах

                # Кастомный процессор: site_name, site_domain и т.д.
                "apps.core.utils.context_processors.site_defaults",

                # Уведомления: notifications_unread_count для колокольчика в шапке.
                # Ленивый (SimpleLazyObject): запрос к БД выполняется только если
                # переменная реально используется в шаблоне, и не более одного раза.
                # Для анонимных пользователей всегда 0 (без запроса к БД).
                "apps.notifications.context_processors.notifications",
            ],
        },
    },
]

# =========================================================
# WSGI / ASGI APPLICATION (ТОЧКИ ВХОДА ДЛЯ СЕРВЕРА)
# =========================================================
WSGI_APPLICATION = "config.wsgi.application"  # Для Gunicorn, uWSGI
ASGI_APPLICATION = "config.asgi.application"  # Для Daphne, Uvicorn (WebSocket)

# =========================================================
# ИНТЕРНАЦИОНАЛИЗАЦИЯ (I18N) И ВРЕМЕННАЯ ЗОНА
# =========================================================
LANGUAGE_CODE = "ru"  # Язык по умолчанию (русский)
TIME_ZONE = "Europe/Minsk"  # Временная зона (Минск, UTC+3)
USE_I18N = True  # Включить интернационализацию
USE_TZ = True  # Использовать временные зоны (вместо naive datetime)

# =========================================================
# СТАТИЧЕСКИЕ ФАЙЛЫ (CSS, JS, ИЗОБРАЖЕНИЯ)
# =========================================================
STATIC_URL = "/static/"  # URL-префикс для статических файлов
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Директория с исходными статическими файлами
]
STATIC_ROOT = BASE_DIR / "static_root"  # Директория для collectstatic (продакшен)

# =========================================================
# МЕДИА-ФАЙЛЫ (ЗАГРУЖЕННЫЕ ПОЛЬЗОВАТЕЛЯМИ)
# =========================================================
MEDIA_URL = "/media/"  # URL-префикс для медиа-файлов
MEDIA_ROOT = BASE_DIR / "media"  # Директория для загруженных файлов

# =========================================================
# DEFAULT AUTO FIELD (ТИП ПОЛЯ ПО УМОЛЧАНИЮ ДЛЯ ID)
# =========================================================
# Django 3.2+: явно указываем тип авто-инкрементного поля
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# EMAIL (ДЛЯ РАЗРАБОТКИ)
# =========================================================
# Console-backend выводит все письма в консоль runserver.
# Позволяет тестировать сброс пароля без настройки SMTP.
#
# Для продакшена заменить на SMTP-бэкенд:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = os.getenv('EMAIL_PORT')
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# EMAIL_USE_TLS = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@yourtune.local'

# =========================================================
# Toast-движок (система всплывающих уведомлений)
# =========================================================
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}



# =========================================================
# CKEDITOR 5 (визуальный редактор юридических документов)
# =========================================================

CKEDITOR_5_CONFIGS = {
    "legal": {
        "language": "ru",
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
            "horizontalLine",
            "|",
            "undo",
            "redo",
        ],
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Обычный текст",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Заголовок 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Заголовок 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "height": "600px",
        "width": "100%",
    },
}