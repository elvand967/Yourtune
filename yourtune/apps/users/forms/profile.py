# apps/users/forms/profile.py
# ==========================================================
# Формы профиля пользователя.
#
# ProfileForm:
#   - редактирует данные CustomUser и Profile;
#   - не работает с файлом аватарки.
#
# AvatarUploadForm:
#   - отдельная форма загрузки аватарки;
#   - используется только UploadAvatarView.
# ==========================================================

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError
from zoneinfo import available_timezones
from apps.users.models import Profile


User = get_user_model()

LANGUAGE_CHOICES = [
    ("ru", "Русский"),
    ("en", "English"),
    ("be", "Беларуская"),
    ("uk", "Українська"),
    ("pl", "Polski"),
]


def get_timezone_choices():
    """
    Формирует список доступных часовых поясов.

    Python/Django используют названия IANA, например:
    Europe/Minsk, Europe/Moscow, UTC.
    """
    timezones = sorted(available_timezones())

    return [
        ("", "Не указывать"),
        *[(timezone_name, timezone_name) for timezone_name in timezones],
    ]

class ProfileForm(forms.ModelForm):
    """
    Комбинированная форма редактирования CustomUser и Profile.

    Аватарка намеренно не входит в эту форму:
    её загрузка выполняется через AvatarUploadForm
    и отдельный маршрут users:upload_avatar.
    """

    first_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Имя"),
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": _("Ваше имя"),
            },
        ),
    )

    middle_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Отчество"),
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": _("Ваше отчество"),
            },
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        label=_("Фамилия"),
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": _("Ваша фамилия"),
            },
        ),
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form__control",
                "placeholder": _("email@example.com"),
            },
        ),
    )

    language = forms.ChoiceField(
        required=False,
        label=_("Язык интерфейса"),
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form__control",
            },
        ),
    )

    timezone = forms.ChoiceField(
        required=False,
        label=_("Часовой пояс"),
        choices=get_timezone_choices,
        widget=forms.Select(
            attrs={
                "class": "form__control",
            },
        ),
    )


    class Meta:
        model = Profile
        fields = [
            "gender",
            "date_of_birth",
            "voice_preference",
            "bio",
            "location",
            "website",
            "language",
            "timezone",
            "is_public",
            "privacy_level",
        ]
        widgets = {
            "gender": forms.Select(
                attrs={
                    "class": "form__control",
                },
            ),
            "date_of_birth": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form__control",
                    "type": "date",
                },
            ),
            "voice_preference": forms.Select(
                attrs={
                    "class": "form__control",
                },
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form__control",
                    "rows": 4,
                    "placeholder": _("Расскажите немного о себе..."),
                    "maxlength": 500,
                },
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form__control",
                    "placeholder": _("Город"),
                },
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "form__control",
                    "placeholder": _("https://example.com"),
                },
            ),
            "is_public": forms.CheckboxInput(
                attrs={
                    "class": "form__choice-input",
                },
            ),
            "privacy_level": forms.Select(
                attrs={
                    "class": "form__control",
                },
            ),
        }
        labels = {
            "gender": _("Пол"),
            "date_of_birth": _("Дата рождения"),
            "voice_preference": _("Предпочтение голоса"),
            "bio": _("О себе"),
            "location": _("Город"),
            "website": _("Сайт"),
            "is_public": _("Публичный профиль"),
            "privacy_level": _("Уровень приватности"),
        }
        help_texts = {
            "bio": _("Максимум 500 символов"),
            "website": _("Ваш личный сайт или портфолио"),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user

        super().__init__(
            *args,
            **kwargs,
        )

        if self.user is not None:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["middle_name"].initial = self.user.middle_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email

    def clean_email(self):
        """
        Проверяет уникальность Email, исключая текущего пользователя.
        """
        email = self.cleaned_data["email"].strip().lower()

        queryset = User.objects.filter(
            email__iexact=email,
        )

        if self.user is not None:
            queryset = queryset.exclude(
                pk=self.user.pk,
            )

        if queryset.exists():
            raise ValidationError(
                _("Пользователь с таким Email уже существует."),
            )

        return email

    def save(self, commit=True):
        """
        Сохраняет данные CustomUser и Profile.

        Аватарка здесь не загружается и не обрабатывается.

        При изменении Email выполняется только синхронизация
        имени уже существующего файла аватарки.
        """
        if self.user is None:
            raise ValueError(
                _("Для ProfileForm необходимо передать пользователя."),
            )

        profile = super().save(
            commit=False,
        )

        old_email = self.user.email.strip().lower()
        new_email = self.cleaned_data["email"].strip().lower()

        self.user.first_name = self.cleaned_data["first_name"].strip()
        self.user.middle_name = self.cleaned_data["middle_name"].strip()
        self.user.last_name = self.cleaned_data["last_name"].strip()
        self.user.email = new_email

        if commit:
            self.user.save()

            profile.save()

            email_changed = old_email != new_email

            if email_changed and profile.avatar:
                profile.sync_avatar_filename(
                    old_email=old_email,
                )

        return profile


class AvatarUploadForm(forms.Form):
    """
    Отдельная форма загрузки аватарки.

    Используется только вместе с UploadAvatarView.
    """

    avatar = forms.FileField(
        label=_("Аватар"),
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
            ),
        ],
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form__control",
                "accept": "image/jpeg,image/png,image/webp",
            },
        ),
    )

    def clean_avatar(self):
        """
        Проверяет размер и корректность изображения.

        Сама обработка, конвертация в JPEG 128×128
        и сохранение выполняются в Profile.upload_avatar().
        """
        avatar = self.cleaned_data.get("avatar")

        if not avatar:
            return avatar

        max_size = 5 * 1024 * 1024

        if avatar.size > max_size:
            raise ValidationError(
                _("Размер изображения не должен превышать 5 МБ."),
            )

        try:
            avatar.seek(0)

            image = Image.open(avatar)
            image.verify()

            avatar.seek(0)

        except (
            UnidentifiedImageError,
            OSError,
        ) as exc:
            raise ValidationError(
                _("Загрузите корректный файл изображения."),
            ) from exc

        return avatar