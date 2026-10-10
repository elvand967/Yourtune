
# yourtune/config/urls.py
# Корневая URL-конфигурация проекта YourTune

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("users/", include("apps.users.urls", namespace="users")),

    path("legal/", include("apps.legal.urls", namespace="legal")),

    path("", include("apps.main.urls", namespace="main")),

    # Маршруты django-ckeditor-5.
    # Нужны для корректной работы визуального редактора в админке.
    path(
        "ckeditor5/",
        include("django_ckeditor_5.urls"),
        name="ck_editor_5_upload_file",
    ),

    # Социальная аутентификация allauth
    path("accounts/", include("allauth.urls")),
]


'''
Django не обслуживает пользовательские медиафайлы автоматически. 
Для разработки нужно добавить маршрут, направляющий MEDIA_URL в MEDIA_ROOT.
'''
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )