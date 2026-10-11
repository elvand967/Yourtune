
# apps/core/urls.py

from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "core"

urlpatterns = [
    path(
        "cookie-policy/",
        TemplateView.as_view(
            template_name="pages/cookie_policy.html"
        ),
        name="cookie_policy"
    ),
    path(
        "api/cookie-consent/",
        views.cookie_consent_api,
        name="cookie_consent_api"
    ),
]
