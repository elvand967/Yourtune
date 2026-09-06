# yourtune/config/wsgi.py

"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
///
Конфигурация WSGI для проекта конфигурации.

Она предоставляет доступ к вызываемой функции WSGI в виде переменной уровня модуля с именем ``application``.

Дополнительную информацию об этом файле см. по ссылке:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
