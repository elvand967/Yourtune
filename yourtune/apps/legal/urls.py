
# apps/legal/urls.py

from django.urls import path
from apps.legal import views

app_name = "legal"

urlpatterns = [
    path(
        "documents/",
        views.LegalDocumentListView.as_view(),
        name="document_list",
    ),

    path(
        "documents/<slug:slug>/",
        views.LegalDocumentDetailView.as_view(),
        name="document_detail",
    ),

    path(
        "accept/",
        views.RequiredConsentView.as_view(),
        name="required_consent",
    ),
]