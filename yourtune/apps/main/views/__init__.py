# apps/main/views/__init__.py
# Импорт всех представлений в одном месте

from .home import home
from .about import about
from .faq import faq
from .blog import blog
from .policy import policy
from .rules import rules

__all__ = [
    'home',
    'about',
    'faq',
    'blog',
    'policy',
    'rules',
]