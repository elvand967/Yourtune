# apps/notifications/views/center.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView

from apps.notifications.categories import Category
from apps.notifications.models import Notification
from apps.notifications.services import Notify
from apps.notifications.views._utils import safe_next_url


class NotificationCenterView(LoginRequiredMixin, ListView):
    template_name = "notifications/center.html"
    context_object_name = "notifications"
    paginate_by = 15

    def get_queryset(self):
        qs = Notification.objects.for_user(self.request.user)

        if self.request.GET.get("status") == "unread":
            qs = qs.unread()

        category = self.request.GET.get("category")
        if category in Category.values:
            qs = qs.filter(category=category)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": _("Центр уведомлений"),
            "categories": Category.choices,
            "current_status": self.request.GET.get("status", ""),
            "current_category": self.request.GET.get("category", ""),
        })

        # Объекты страницы уже загружены с is_read=False → маркер «Новое»
        # будет виден в этом рендере. В БД помечаем одним UPDATE.
        unread_ids = [n.pk for n in context["page_obj"] if not n.is_read]
        if unread_ids:
            Notification.objects.filter(pk__in=unread_ids).update(
                is_read=True, read_at=timezone.now(),
            )
        return context


class MarkAllReadView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request):
        updated = Notification.objects.for_user(request.user).mark_read()

        # persist=False: иначе «всё прочитано» создаст новое непрочитанное
        if updated:
            Notify.success(
                request, _("Готово"),
                _("Отмечено как прочитанные: %(count)d.") % {"count": updated},
                persist=False,
            )
        else:
            Notify.info(request, _("Непрочитанных уведомлений нет."), persist=False)

        return redirect(safe_next_url(request))


class MarkReadView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        return redirect(safe_next_url(request))


class NotificationOpenView(LoginRequiredMixin, View):
    """Клик по уведомлению: отметить прочитанным и перейти по ссылке действия."""

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()

        if notification.url and url_has_allowed_host_and_scheme(
            notification.url, allowed_hosts={request.get_host()},
        ):
            return redirect(notification.url)
        return redirect("notifications:center")