
# apps/notifications/urls.py

from django.urls import path

from apps.notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationCenterView.as_view(), name="center"),
    path("mark-all-read/", views.MarkAllReadView.as_view(), name="mark_all_read"),
    path("<uuid:pk>/read/", views.MarkReadView.as_view(), name="mark_read"),
    path("<uuid:pk>/open/", views.NotificationOpenView.as_view(), name="open"),
]