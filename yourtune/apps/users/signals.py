# apps/users/signals.py
# =====================

import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.users.models import Profile


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(
    post_save,
    sender=User,
    dispatch_uid="users.create_profile_for_user",
)
def create_profile_for_user(
    sender,
    instance,
    created,
    raw,
    **kwargs,
):
    """
    Создаёт профиль для нового пользователя.

    Аватарка создаётся после успешного завершения
    транзакции базы данных.
    """
    if raw or not created:
        return

    profile = Profile.objects.create(
        user=instance,
    )

    transaction.on_commit(
        lambda profile_id=profile.pk: generate_initial_avatar(
            profile_id,
        )
    )


def generate_initial_avatar(profile_id):
    """
    Генерирует стандартную аватарку профиля.

    Функция повторно получает профиль из базы,
    чтобы callback не хранил объект модели в памяти
    дольше необходимого.
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
            "Ошибка генерации начальной аватарки "
            "для профиля %s.",
            profile_id,
        )


@receiver(
    post_delete,
    sender=Profile,
    dispatch_uid="users.delete_profile_avatar_file",
)
def delete_profile_avatar_file(
    sender,
    instance,
    **kwargs,
):
    """
    Удаляет физический файл аватарки
    после удаления профиля.
    """
    if not instance.avatar:
        return

    try:
        instance.avatar.delete(
            save=False,
        )
    except Exception:
        logger.exception(
            "Ошибка удаления аватарки профиля %s.",
            instance.pk,
        )