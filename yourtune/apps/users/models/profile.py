# apps/users/models/profile.py
# ============================

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDModel
from apps.users.utils.avatar import (
    avatar_upload_to,
    delete_storage_file,
    generate_avatar_image,
    get_avatar_filename,
    process_uploaded_avatar,
)
from apps.users.utils.storages import OverwriteStorage


avatar_storage = OverwriteStorage()


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

    class PrivacyLevel(models.TextChoices):
        PUBLIC = "public", _("Публичный")
        FRIENDS = "friends", _("Только друзья")
        PRIVATE = "private", _("Приватный")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Пользователь"),
    )

    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        storage=avatar_storage,
        blank=True,
        default="",
        verbose_name=_("Аватар"),
        help_text=_(
            "Изображение будет автоматически преобразовано "
            "в JPEG 128×128"
        ),
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

    privacy_level = models.CharField(
        max_length=10,
        choices=PrivacyLevel.choices,
        default=PrivacyLevel.PUBLIC,
        verbose_name=_("Уровень приватности"),
    )

    class Meta:
        verbose_name = _("Профиль пользователя")
        verbose_name_plural = _("Профили пользователей")
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return self.user.email

    @property
    def avatar_path(self):
        """
        Возвращает относительный путь текущей аватарки.
        """
        if not self.avatar:
            return ""

        return self.avatar.name

    def _save_avatar_content(self, content):
        """
        Сохраняет содержимое аватарки под единым именем.

        Старый файл не удаляется внутри этого метода.
        Это позволяет сначала успешно сохранить новый файл,
        а затем удалить старый.
        """
        target_name = avatar_upload_to(
            self,
            content.name,
        )

        saved_name = self.avatar.storage.save(
            target_name,
            content,
        )

        self.avatar.name = saved_name
        self.save(
            update_fields=["avatar", "updated_at"],
        )

        return saved_name

    @transaction.atomic
    def save_default_avatar(self):
        """
        Создаёт или заменяет аватарку автоматически
        с использованием имени и фамилии либо Email.
        """
        old_name = self.avatar_path

        content = generate_avatar_image(
            self.user,
        )

        new_name = self._save_avatar_content(content)

        if old_name and old_name != new_name:
            delete_storage_file(old_name)

        return new_name

    @transaction.atomic
    def upload_avatar(self, uploaded_file):
        """
        Обрабатывает и сохраняет пользовательскую аватарку.

        На выходе файл будет:

        - JPEG;
        - 128×128;
        - с единым именем;
        - в каталоге по году регистрации.
        """
        processed_content = process_uploaded_avatar(
            uploaded_file,
            self.user,
        )

        old_name = self.avatar_path

        new_name = self._save_avatar_content(
            processed_content,
        )

        if old_name and old_name != new_name:
            delete_storage_file(old_name)

        return new_name

    @transaction.atomic
    def reset_avatar(self):
        """
        Заменяет текущую аватарку на автоматически
        сгенерированную.
        """
        return self.save_default_avatar()

    @transaction.atomic
    def sync_avatar_filename(self, old_email):
        """
        Пересохраняет текущую аватарку под именем,
        соответствующим новому Email пользователя.

        Сама фотография не генерируется заново.
        """
        if not self.avatar:
            return self.save_default_avatar()

        old_name = self.avatar_path

        content = self.avatar.storage.open(
            old_name,
            mode="rb",
        )

        try:
            processed_content = process_uploaded_avatar(
                content,
                self.user,
            )
        finally:
            content.close()

        new_name = self._save_avatar_content(
            processed_content,
        )

        if old_name and old_name != new_name:
            delete_storage_file(old_name)

        return new_name

    def delete_avatar_file(self):
        """
        Удаляет физический файл аватарки,
        но не удаляет запись профиля.
        """
        old_name = self.avatar_path

        if old_name:
            delete_storage_file(old_name)

        self.avatar = ""
        self.save(
            update_fields=["avatar", "updated_at"],
        )