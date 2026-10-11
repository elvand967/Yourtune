
# apps/core/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from apps.core.models import CookieConsent


@receiver(user_logged_in)
def attach_cookie_consents_to_user(
    sender,
    request,
    user,
    **kwargs,
):
    """
    Привязывает анонимные cookie-согласия текущей сессии
    к пользователю после входа или регистрации.
    """
    session_key = request.session.session_key

    if not session_key:
        return

    CookieConsent.objects.filter(
        session_key=session_key,
        user__isnull=True,
    ).update(user=user)