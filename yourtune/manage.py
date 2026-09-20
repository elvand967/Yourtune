#!/usr/bin/env python
"""Утилита командной строки Django для выполнения административных задач."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


"""
.env загружается один раз в manage.py, а settings/__init__.py только выбирает dev/prod по DJANGO_ENV.
Это самый прозрачный вариант: переменные окружения доступны до импорта Django settings,
и сама конфигурация остаётся без лишней магии.
"""
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def main():
    """Run administrative tasks. / Выполнение административных задач."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and / Не удалось импортировать Django. Вы уверены, что он установлен? "
            "available on your PYTHONPATH environment variable? Did you / Доступен ли он в вашей переменной среды PYTHONPATH? Вы его добавили? "
            "forget to activate a virtual environment? / Забыли активировать виртуальную среду?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
