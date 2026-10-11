
# apps/core/views/cookie_consent.py
#==================================

"""
API для сохранения cookie-согласия пользователя YourTune.

Согласие сохраняется только для авторизованных пользователей.
Для гостей сайт использует исключительно необходимые cookie
и не создаёт записей в базе данных.
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.models import CookieConsent


@csrf_exempt
@require_POST
def cookie_consent_api(request):
    """
    Сохраняет выбранную пользователем конфигурацию cookie.

    Ожидаемый JSON:
    {
        "necessary": true,
        "analytics": true,
        "marketing": false,
        "policy_version": "1.0",
        "source": "settings"
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "detail": (
                    "Согласие на использование cookie может сохранить "
                    "только авторизованный пользователь."
                )
            },
            status=401,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"detail": "Некорректный JSON."},
            status=400,
        )

    source = data.get("source", "settings")

    if source not in CookieConsent.ConsentSource.values:
        source = CookieConsent.ConsentSource.SETTINGS

    consent = CookieConsent.objects.create(
        user=request.user,
        session_key=request.session.session_key or "",
        necessary=True,
        analytics=bool(data.get("analytics", False)),
        marketing=bool(data.get("marketing", False)),
        policy_version=str(
            data.get("policy_version", "1.0")
        ),
        source=(
            CookieConsent.ConsentSource.SETTINGS
            if data.get("source") == "settings"
            else CookieConsent.ConsentSource.BANNER
        ),
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return JsonResponse(
        {
            "detail": "Согласие сохранено.",
            "consent_id": consent.id,
            "analytics": consent.analytics,
            "marketing": consent.marketing,
            "policy_version": consent.policy_version,
        }
    )