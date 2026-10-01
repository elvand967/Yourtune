# yourtune/apps/users/views/profile.py
# ====================================

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.views import View

from apps.users.forms.profile import ProfileForm
from apps.users.models import Profile


logger = logging.getLogger(__name__)


class ProfileViewMixin(LoginRequiredMixin):
    """
    Общая логика представлений профиля.
    """

    profile_model = Profile

    def get_profile(self, user):
        """
        Возвращает профиль пользователя.

        Если профиль отсутствует, он создаётся автоматически.
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
        Запланировать генерацию аватарки после успешного
        завершения транзакции базы данных.
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
    Отображает подробную информацию о профиле
    текущего авторизованного пользователя.
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
    Отображает и обрабатывает форму редактирования профиля.

    Изменяемые данные:

    - имя;
    - отчество;
    - фамилия;
    - Email;
    - пол;
    - дата рождения;
    - предпочтение голоса;
    - описание;
    - город;
    - сайт;
    - язык;
    - часовой пояс;
    - публичность профиля;
    - уровень приватности.
    """

    template_name = "users/profile/edit.html"
    success_url = "users:profile_detail"

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

                messages.error(
                    request,
                    str(exc),
                )

            except Exception:
                logger.exception(
                    "Ошибка сохранения профиля пользователя %s.",
                    request.user.pk,
                )

                messages.error(
                    request,
                    "Не удалось сохранить профиль. "
                    "Попробуйте ещё раз.",
                )

            else:
                messages.success(
                    request,
                    "Профиль успешно обновлён.",
                )

                return redirect(
                    self.success_url,
                )
        else:
            messages.error(
                request,
                "Исправьте ошибки в форме.",
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

        uploaded_file = request.FILES.get(
            "avatar",
        )

        if not uploaded_file:
            messages.error(
                request,
                "Выберите изображение для загрузки.",
            )

            return redirect(
                "users:profile_edit",
            )

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

            messages.error(
                request,
                str(exc),
            )

        except Exception:
            logger.exception(
                "Ошибка загрузки аватарки пользователя %s.",
                request.user.pk,
            )

            messages.error(
                request,
                "Не удалось загрузить аватарку.",
            )

        else:
            messages.success(
                request,
                "Аватарка успешно обновлена.",
            )

        return redirect(
            "users:profile_edit",
        )


class ResetAvatarView(ProfileViewMixin, View):
    """
    Сбрасывает текущую аватарку на автоматически
    сгенерированную.
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

            messages.error(
                request,
                "Не удалось сбросить аватарку.",
            )

        else:
            messages.success(
                request,
                "Аватарка сброшена на стандартную.",
            )

        return redirect(
            "users:profile_edit",
        )


def generate_missing_avatar(profile_id):
    """
    Создаёт стандартную аватарку профиля,
    если аватарка отсутствует.
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