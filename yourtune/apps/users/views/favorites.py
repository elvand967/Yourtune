# apps/users/views/favorites.py
"""
Views для управления избранным пользователя.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from apps.users.models import Favorite


class FavoritesListView(LoginRequiredMixin, ListView):
    """
    Список избранного пользователя.
    """
    model = Favorite
    template_name = 'users/favorites/list.html'
    context_object_name = 'favorites'
    ordering = ['-created_at']

    def get_queryset(self):
        """Возвращает только избранное текущего пользователя."""
        return Favorite.objects.filter(user=self.request.user).select_related(
            'content_type'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Избранное')
        return context