# apps/users/views/playlists.py
# =====================================

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class PlaylistListView(LoginRequiredMixin, TemplateView):
    """Список плейлистов пользователя."""
    template_name = 'users/playlists/list.html'


class FavoritesView(LoginRequiredMixin, TemplateView):
    """Избранное пользователя."""
    template_name = 'users/playlists/favorites.html'