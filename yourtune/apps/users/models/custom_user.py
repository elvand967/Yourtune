
# apps/users/models/custom_user.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from apps.core.models import UUIDModel
from apps.users.utils.managers import CustomUserManager

"""
Кастомная модель пользователя для проекта yourtune.

Назначение:
- Использовать email как основной идентификатор входа в систему.
- Поддерживать полноценную интеграцию с Django auth.
- Быть базой для будущих расширений: профиль, соц. авторизация, тарифы,
  история действий, верификация email и т.д.

Почему AbstractBaseUser:
- Даёт полный контроль над набором полей.
- Позволяет использовать email вместо username.
- Требует явного менеджера, USERNAME_FIELD и admin-настройки.
- Подходит, когда стандартный User/AbstractUser уже тесен по архитектуре.

Почему UUIDModel:
- UUID в качестве primary key удобен для публичных ссылок, интеграций
  и снижает предсказуемость идентификаторов.
- Хорошо вписывается в модульную и расширяемую архитектуру.

Поля:
- email: основной логин пользователя, обязателен и уникален.
- first_name: имя пользователя.
- middle_name: отчество пользователя.
- last_name: фамилия пользователя.
- is_staff: доступ к административной панели Django.
- is_active: активен ли аккаунт.

Менеджер:
- objects = CustomUserManager()
- Отвечает за create_user() и create_superuser().
- Нормализует email и корректно задаёт пароль через set_password().

Важные настройки Django:
- AUTH_USER_MODEL = "users.CustomUser" (yourtune/config/settings/base.py) должен быть задан до первой миграции.
- USERNAME_FIELD = "email" сообщает Django, что email — поле входа.
- EMAIL_FIELD = "email" явно указывает основное email-поле модели.
- REQUIRED_FIELDS определяет дополнительные поля для createsuperuser.

Важно:
- Тарифы, подписки, лимиты и биллинг не стоит хранить здесь.
  Это отдельный домен и лучше выносить в отдельные модели.
- Профиль пользователя тоже лучше держать отдельно, через OneToOneField
  в модели Profile.
"""
class CustomUser(UUIDModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ в админку")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_verified = models.BooleanField(default=False, verbose_name="Email подтвержден")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        full_name = " ".join(
            part for part in [self.first_name, self.middle_name, self.last_name] if part
        ).strip()
        return full_name or self.email

    def get_full_name(self):
        return " ".join(
            part for part in [self.first_name, self.middle_name, self.last_name] if part
        ).strip()

    def get_short_name(self):
        return self.first_name or self.email