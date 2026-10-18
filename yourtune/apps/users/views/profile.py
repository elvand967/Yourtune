# apps/users/views/profile.py
# ==========================================================
# Представления профиля пользователя.
#
# ProfileDetailView — просмотр профиля.
# ProfileUpdateView — редактирование данных без аватарки.
# UploadAvatarView  — отдельная загрузка аватарки.
# ResetAvatarView   — сброс аватарки.
# ==========================================================

import logging

from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.legal.mixins import ConsentRequiredMixin
from apps.notifications.categories import Category
from apps.notifications.services import Notify
from apps.users.forms.profile import AvatarUploadForm, ProfileForm
from apps.users.models import Profile


logger = logging.getLogger(__name__)


class ProfileViewMixin(ConsentRequiredMixin):
    """
    Общая логика представлений профиля.
    """

    profile_model = Profile

    def get_profile(self, user):
        """
        Возвращает профиль пользователя,
        при необходимости создавая его.
        """
        profile, created = self.profile_model.objects.get_or_create(
            user=user,
        )

        if created:
            self.schedule_avatar_generation(
                profile.pk,
            )

        return profile

    @staticmethod
    def schedule_avatar_generation(profile_id):
        """
        Создаёт аватарку после фиксации транзакции,
        если у нового профиля ещё нет файла.
        """
        transaction.on_commit(
            lambda: generate_missing_avatar(profile_id),
        )

    def get_profile_context(self, request, profile, form=None):
        """
        Формирует общий контекст шаблонов профиля.
        """
        return {
            "user": request.user,
            "profile": profile,
            "form": form,
            "email_not_verified": not request.user.is_verified,
            "email_verified": request.user.is_verified,
        }


class ProfileDetailView(ProfileViewMixin, View):
    """
    Отображает подробную информацию о профиле.
    """

    template_name = "users/profile/detail.html"

    def get(self, request):
        profile = self.get_profile(
            request.user,
        )

        context = self.get_profile_context(
            request,
            profile,
        )

        return render(
            request,
            self.template_name,
            context,
        )


class ProfileUpdateView(ProfileViewMixin, View):
    """
    Редактирует данные пользователя и профиля.

    Не обрабатывает загрузку аватарки:
    для этого используется UploadAvatarView.
    """

    template_name = "users/profile/edit.html"
    success_url = reverse_lazy("users:profile_detail")

    def get_form(self, request, profile):
        """
        Создаёт форму редактирования профиля.
        """
        return ProfileForm(
            data=request.POST or None,
            instance=profile,
            user=request.user,
        )

    def get(self, request):
        profile = self.get_profile(
            request.user,
        )

        form = self.get_form(
            request,
            profile,
        )

        context = self.get_profile_context(
            request,
            profile,
            form,
        )

        return render(
            request,
            self.template_name,
            context,
        )

    def post(self, request):
        profile = self.get_profile(
            request.user,
        )

        form = self.get_form(
            request,
            profile,
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

            except ValueError as exc:
                logger.warning(
                    "Ошибка обработки профиля пользователя %s: %s",
                    request.user.pk,
                    exc,
                )

                Notify.error(
                    request,
                    title=_("Не удалось сохранить профиль"),
                    message=str(exc),
                    persist=False,
                    category=Category.ACCOUNT,
                )

            except Exception:
                logger.exception(
                    "Ошибка сохранения профиля пользователя %s.",
                    request.user.pk,
                )

                Notify.error(
                    request,
                    title=_("Не удалось сохранить профиль"),
                    message=_(
                        "Произошла непредвиденная ошибка. "
                        "Попробуйте ещё раз."
                    ),
                    persist=False,
                    category=Category.ACCOUNT,
                )

            else:
                Notify.success(
                    request,
                    title=_("Профиль обновлён"),
                    message=_("Изменения успешно сохранены."),
                    persist=False,
                    category=Category.ACCOUNT,
                )

                return redirect(
                    self.success_url,
                )

        else:
            Notify.error(
                request,
                title=_("Проверьте форму"),
                message=_(
                    "Исправьте выделенные ошибки и попробуйте снова."
                ),
                persist=False,
                category=Category.ACCOUNT,
            )

        context = self.get_profile_context(
            request,
            profile,
            form,
        )

        return render(
            request,
            self.template_name,
            context,
        )


class UploadAvatarView(ProfileViewMixin, View):
    """
    Обрабатывает отдельную загрузку аватарки.
    """

    def post(self, request):
        profile = self.get_profile(
            request.user,
        )

        form = AvatarUploadForm(
            data=request.POST,
            files=request.FILES,
        )

        if not form.is_valid():
            errors = form.errors.get("avatar")

            message = (
                errors[0]
                if errors
                else _("Выберите корректное изображение.")
            )

            Notify.error(
                request,
                title=_("Не удалось загрузить аватарку"),
                message=message,
                persist=False,
                category=Category.ACCOUNT,
            )

            return redirect(
                "users:profile_edit",
            )

        uploaded_file = form.cleaned_data["avatar"]

        try:
            with transaction.atomic():
                profile.upload_avatar(
                    uploaded_file,
                )

        except ValueError as exc:
            logger.warning(
                "Ошибка обработки аватарки пользователя %s: %s",
                request.user.pk,
                exc,
            )

            Notify.error(
                request,
                title=_("Не удалось загрузить аватарку"),
                message=str(exc),
                persist=False,
                category=Category.ACCOUNT,
            )

        except Exception:
            logger.exception(
                "Ошибка загрузки аватарки пользователя %s.",
                request.user.pk,
            )

            Notify.error(
                request,
                title=_("Не удалось загрузить аватарку"),
                message=_(
                    "Произошла непредвиденная ошибка. "
                    "Попробуйте ещё раз."
                ),
                persist=False,
                category=Category.ACCOUNT,
            )

        else:
            Notify.success(
                request,
                title=_("Аватарка обновлена"),
                message=_("Новое изображение профиля сохранено."),
                persist=False,
                category=Category.ACCOUNT,
            )

        return redirect(
            "users:profile_edit",
        )


class ResetAvatarView(ProfileViewMixin, View):
    """
    Сбрасывает текущую аватарку
    на автоматически сгенерированную.
    """

    def post(self, request):
        profile = self.get_profile(
            request.user,
        )

        try:
            with transaction.atomic():
                profile.reset_avatar()

        except Exception:
            logger.exception(
                "Ошибка сброса аватарки пользователя %s.",
                request.user.pk,
            )

            Notify.error(
                request,
                title=_("Не удалось сбросить аватарку"),
                message=_(
                    "Произошла непредвиденная ошибка. "
                    "Попробуйте ещё раз."
                ),
                persist=False,
                category=Category.ACCOUNT,
            )

        else:
            Notify.success(
                request,
                title=_("Аватарка сброшена"),
                message=_("Установлена стандартная аватарка."),
                persist=False,
                category=Category.ACCOUNT,
            )

        return redirect(
            "users:profile_edit",
        )


def generate_missing_avatar(profile_id):
    """
    Создаёт стандартную аватарку,
    если у профиля она отсутствует.
    """
    try:
        profile = Profile.objects.select_related(
            "user",
        ).get(
            pk=profile_id,
        )

        if not profile.avatar:
            profile.save_default_avatar()

    except Profile.DoesNotExist:
        logger.warning(
            "Профиль %s не найден при генерации аватарки.",
            profile_id,
        )

    except Exception:
        logger.exception(
            "Ошибка генерации аватарки профиля %s.",
            profile_id,
        )