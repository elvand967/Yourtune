
# apps/notifications/context_processors.py

from django.utils.functional import SimpleLazyObject

from apps.notifications.models import Notification


def notifications(request):
    """
    notifications_unread_count — запрос в БД выполняется только если
    переменная реально используется в шаблоне, и не более одного раза.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"notifications_unread_count": 0}

    return {
        "notifications_unread_count": SimpleLazyObject(
            lambda: Notification.objects.for_user(user).unread().count()
        ),
    }