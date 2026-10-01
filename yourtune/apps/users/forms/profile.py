# apps/users/forms/profile.py
# ==========================

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image, UnidentifiedImageError

from apps.users.models import Profile
from apps.users.utils.avatar import process_uploaded_avatar


User = get_user_model()


class ProfileForm(forms.ModelForm):
    """
    Комбинированная форма редактирования CustomUser и Profile.

    Поля пользователя:
    - first_name;
    - middle_name;
    - last_name;
    - email.

    Поля профиля:
    - avatar;
    - gender;
    - date_of_birth;
    - voice_preference;
    - bio;
    - location;
    - website;
    - language;
    - timezone;
    - is_public;
    - privacy_level.
    """

    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Имя",
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": "Ваше имя",
            },
        ),
    )

    middle_name = forms.CharField(
        max_length=150,
        required=False,
        label="Отчество",
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": "Ваше отчество",
            },
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Фамилия",
        widget=forms.TextInput(
            attrs={
                "class": "form__control",
                "placeholder": "Ваша фамилия",
            },
        ),
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form__control",
                "placeholder": "email@example.com",
            },
        ),
    )

    class Meta:
        model = Profile
        fields = [
            "avatar",
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
        validators = [
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
            ),
        ]
        widgets = {
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form__control",
                    "accept": "image/jpeg,image/png,image/webp",
                },
            ),
            "gender": forms.Select(
                attrs={
                    "class": "form__control",
                },
            ),
            "date_of_birth": forms.DateInput(
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
                    "placeholder": "Расскажите немного о себе...",
                    "maxlength": 500,
                },
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form__control",
                    "placeholder": "Город",
                },
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "form__control",
                    "placeholder": "https://example.com",
                },
            ),
            "language": forms.Select(
                attrs={
                    "class": "form__control",
                },
            ),
            "timezone": forms.Select(
                attrs={
                    "class": "form__control",
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
            "avatar": "Аватар",
            "gender": "Пол",
            "date_of_birth": "Дата рождения",
            "voice_preference": "Предпочтение голоса",
            "bio": "О себе",
            "location": "Город",
            "website": "Сайт",
            "language": "Язык интерфейса",
            "timezone": "Часовой пояс",
            "is_public": "Публичный профиль",
            "privacy_level": "Уровень приватности",
        }
        help_texts = {
            "avatar": (
                "Изображение будет преобразовано "
                "в JPEG 128×128"
            ),
            "bio": "Максимум 500 символов",
            "website": "Ваш личный сайт или портфолио",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user

        super().__init__(
            *args,
            **kwargs,
        )

        if self.user is not None:
            self.fields["first_name"].initial = (
                self.user.first_name
            )
            self.fields["middle_name"].initial = (
                self.user.middle_name
            )
            self.fields["last_name"].initial = (
                self.user.last_name
            )
            self.fields["email"].initial = (
                self.user.email
            )

    def clean_email(self):
        """
        Проверяет уникальность Email.

        Текущий пользователь исключается из проверки.
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
                "Пользователь с таким Email уже существует.",
            )

        return email

    def clean_avatar(self):
        """
        Проверяет загруженный файл без изменения его содержимого.

        Фактическая обработка выполняется в save(),
        когда уже известен пользователь.
        """
        avatar = self.cleaned_data.get("avatar")

        if not avatar:
            return avatar

        max_size = 5 * 1024 * 1024

        if avatar.size > max_size:
            raise ValidationError(
                "Размер изображения не должен превышать 5 МБ.",
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
                "Загрузите корректный файл изображения.",
            ) from exc

        return avatar

    def save(self, commit=True, user=None):
        """
        Сохраняет Profile и CustomUser.

        Параметр user можно передать явно либо использовать
        пользователя, переданного в конструктор формы.
        """
        current_user = user or self.user

        if current_user is None:
            raise ValueError(
                "Для ProfileForm необходимо передать пользователя.",
            )

        profile = super().save(
            commit=False,
        )

        old_email = current_user.email.strip().lower()
        new_email = self.cleaned_data["email"].strip().lower()

        current_user.first_name = (
            self.cleaned_data["first_name"].strip()
        )
        current_user.middle_name = (
            self.cleaned_data["middle_name"].strip()
        )
        current_user.last_name = (
            self.cleaned_data["last_name"].strip()
        )
        current_user.email = new_email

        if commit:
            current_user.save()

            uploaded_avatar = self.cleaned_data.get("avatar")

            if uploaded_avatar:
                profile.upload_avatar(
                    uploaded_avatar,
                )
            elif old_email != new_email:
                profile.sync_avatar_filename(
                    old_email=old_email,
                )
            else:
                profile.save()

        return profile