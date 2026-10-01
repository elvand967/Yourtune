
# yourtune/config/urls.py
# Корневой URL-конфигурация проекта YourTune

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Админ-панель Django
    path("admin/", admin.site.urls),

    # Allauth URLs (без namespace!)
    path('accounts/', include('allauth.urls')),

    # Основное приложение (главная, о проекте, FAQ, блог)
    path("", include("apps.main.urls")),

    # Приложение пользователей (профиль, настройки, избранное)
    path("users/", include("apps.users.urls")),
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