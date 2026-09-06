# yourtune/config/asgi.py

"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
///
Конфигурация ASGI для проекта конфигурации.

Она предоставляет доступ к вызываемой функции ASGI в виде переменной уровня модуля с именем ``application``.

Дополнительную информацию об этом файле см. по ссылке:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
