
# yourtune/config/settings/base.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Пути внутри проекта следует создавать следующим образом: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# Настройки для быстрого запуска разработки — непригодны для использования в производственной среде.
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

load_dotenv()  # Загружает переменные из .env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production! - ???
DEBUG = os.getenv('DEBUG') == 'True'



# Авторизация
'''
Если применяется кастомная модель, до создания любых миграций,
подготовить к миграции class CustomUser(UUIDModel, AbstractBaseUser, PermissionsMixin)
и произвести при первой миграции, предварительно указав:  AUTH_USER_MODEL =  'users.CustomUser'
чтобы Django понимал, что используется именно ваша модель.
'''
AUTH_USER_MODEL = "users.CustomUser"


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # логика allauth:
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Кастомные провайдеры (после allauth!)
    'apps.users.providers.yandex',


    # кастомные пакеты:
    "apps.core.apps.CoreConfig",
    "apps.users.apps.UsersConfig",
    'apps.main.apps.MainConfig',
]


# =========================================================
# Allauth settings
# =========================================================

SITE_ID = 1

# Бэкенды аутентификации
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# =========================================================
# Account settings (email-аутентификация)
# =========================================================

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True

# Отключаем username
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False

# =========================================================
# Social account settings (авто-связывание по email)
# =========================================================

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'

# Автоматическое связывание существующих аккаунтов по email
SOCIALACCOUNT_ADAPTER = 'apps.users.adapters.CustomSocialAccountAdapter'

# Отключаем промежуточную страницу (bridge page)
SOCIALACCOUNT_LOGIN_ON_REDIRECT = True

# =========================================================
# Переопределение форм
# =========================================================

ACCOUNT_FORMS = {
    'login': 'apps.users.forms.auth.CustomLoginForm',
    'signup': 'apps.users.forms.auth.CustomSignupForm',
}

SOCIALACCOUNT_FORMS = {
    'signup': 'apps.users.forms.auth.CustomSocialSignupForm',
}

# =========================================================
# Провайдеры
# =========================================================

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'VERIFIED_EMAIL': True,
    },
    'yandex': {
        'SCOPE': ['login:email', 'login:info'],
    },
}

# =========================================================
# URL redirects
# =========================================================

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:profile_detail'
LOGOUT_REDIRECT_URL = 'main:home'
# =========================================================


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "apps.core.utils.context_processors.site_defaults",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"



LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Minsk"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "static_root"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# OAuth credentials (из переменных окружения)
# import os    # импортирован в начале config/settings/base.py
from dotenv import load_dotenv

load_dotenv()

SOCIALACCOUNT_GOOGLE_CLIENT_ID = os.getenv('SOCIALACCOUNT_GOOGLE_CLIENT_ID', '')
SOCIALACCOUNT_GOOGLE_SECRET = os.getenv('SOCIALACCOUNT_GOOGLE_SECRET', '')

SOCIALACCOUNT_YANDEX_CLIENT_ID = os.getenv('SOCIALACCOUNT_YANDEX_CLIENT_ID', '')
SOCIALACCOUNT_YANDEX_SECRET = os.getenv('SOCIALACCOUNT_YANDEX_SECRET', '')