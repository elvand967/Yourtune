# apps/main/views/blog.py
# Представления для страницы блога

from django.shortcuts import render


def blog(request):
    """Страница 'Блог'."""
    context = {
        'title': 'Блог и статьи',
        'description': 'Практики, объяснения и полезные материалы о работе с аффирмациями.',

        'articles': [
            {
                'title': 'Как использовать аффирмации каждый день',
                'description': 'Простые правила и рекомендации для ежедневной практики.',
                'url': '#',
                'category': 'Практика',
                'style': 'violet',
                'author': 'Анна Петрова',
                'published_date': '2026-09-01',
            },
            {
                'title': 'Практика возвращения к спокойствию',
                'description': 'Техники быстрого снятия стресса и напряжения.',
                'url': '#',
                'category': 'Медитация',
                'style': 'blue',
                'author': 'Михаил Иванов',
                'published_date': '2026-08-25',
            },
        ],

        'categories': [
            {'name': 'Практика', 'url': '#', 'count': 12},
            {'name': 'Медитация', 'url': '#', 'count': 8},
            {'name': 'Психология', 'url': '#', 'count': 15},
            {'name': 'Забота о себе', 'url': '#', 'count': 10},
        ],
    }
    return render(request, 'main/blog.html', context)