
# apps/users/models/profile.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from apps.core.models import UUIDModel


def avatar_upload_to(instance, filename):
    return f"avatars/user_{instance.user_id}/{filename}"


class Profile(UUIDModel):
    class Gender(models.TextChoices):
        FEMALE = "female", _("Женский")
        MALE = "male", _("Мужской")
        OTHER = "other", _("Другое")
        NOT_SET = "not_set", _("Не указывать")

    class VoicePreference(models.TextChoices):
        FEMALE = "female", _("Женская озвучка")
        MALE = "male", _("Мужская озвучка")
        NEUTRAL = "neutral", _("Нейтральная озвучка")
        AUTO = "auto", _("Подобрать автоматически")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Пользователь"),
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        verbose_name=_("Аватар"),
        help_text=_("Рекомендуется квадратное изображение"),
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.NOT_SET,
        verbose_name=_("Пол"),
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Дата рождения"),
    )

    voice_preference = models.CharField(
        max_length=10,
        choices=VoicePreference.choices,
        default=VoicePreference.AUTO,
        verbose_name=_("Предпочтение голоса"),
    )

    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        verbose_name=_("О себе"),
    )

    location = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name=_("Город"),
    )

    website = models.URLField(
        blank=True,
        default="",
        verbose_name=_("Сайт"),
    )

    language = models.CharField(
        max_length=10,
        blank=True,
        default="ru",
        verbose_name=_("Язык интерфейса"),
    )

    timezone = models.CharField(
        max_length=64,
        blank=True,
        default="Europe/Minsk",
        verbose_name=_("Часовой пояс"),
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name=_("Публичный профиль"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлён"))

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")

    def __str__(self):
        return self.user.email