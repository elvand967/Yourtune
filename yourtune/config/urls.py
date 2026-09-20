
# yourtune/config/urls.py
# Корневой URL-конфигурация проекта YourTune

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Админ-панель Django
    path("admin/", admin.site.urls),

    # Allauth (регистрация, вход, выход)
    # path("accounts/", include("allauth.urls")),

    # Основное приложение (главная, о проекте, FAQ, блог)
    path("", include("apps.main.urls")),

    # Приложение пользователей (профиль, настройки, избранное)
    # path("users/", include("apps.users.urls")),
]