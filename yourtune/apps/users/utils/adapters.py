# apps/users/utils/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RouteMasterSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Кастомный адаптер для yourtune.
    Автоматически связывает вход через социальную сеть с существующим email-аккаунтом.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Вызывается непосредственно перед тем, как пользователь логинится через соцсеть.
        """
        # Если социальный аккаунт уже связан с пользователем в БД, ничего не делаем
        if sociallogin.is_existing:
            return

        # Получаем email из данных, которые вернул провайдер (Google, VK, Yandex и т.д.)
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            # Ищем существующего пользователя по email
            existing_user = User.objects.get(email__iexact=email)

            # Связываем социальный аккаунт с найденным пользователем
            sociallogin.connect(request, existing_user)

        except User.DoesNotExist:
            # Если пользователя с таким email нет, allauth продолжит стандартную регистрацию
            pass


class RouteMasterAccountAdapter(DefaultAccountAdapter):
    """
    Кастомный адаптер для обычных аккаунтов.
    Управляет уведомлениями и логикой отправки стандартных писем.
    """

    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        """
        Перехватывает стандартные уведомления allauth и добавляет напоминание про Спам.
        """
        # Проверяем шаблон успешной отправки письма подтверждения
        if message_template == 'account/messages/email_confirmation_sent.txt':
            custom_message = _(
                "На ваш Email отправлено письмо со ссылкой для подтверждения. "
                "Если вы не получили его в течение пары минут, **пожалуйста, проверьте папку СПАМ**."
            )
            return messages.add_message(request, messages.INFO, custom_message, extra_tags=extra_tags)

        # Для всех остальных системных сообщений сохраняем стандартное поведение allauth
        return super().add_message(request, level, message_template, message_context, extra_tags)
