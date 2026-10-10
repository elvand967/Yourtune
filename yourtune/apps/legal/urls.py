
# apps/legal/urls.py

from django.urls import path
from apps.legal import views


app_name = "legal"


urlpatterns = [
    path(
        "policy/",
        views.PolicyDetailView.as_view(),
        name="policy",
    ),

    path(
        "rules/",
        views.TermsDetailView.as_view(),
        name="rules",
    ),

    path(
        "accept/",
        views.RequiredConsentView.as_view(),
        name="required_consent",
    ),
]