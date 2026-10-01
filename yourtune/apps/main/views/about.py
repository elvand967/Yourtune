# apps/main/views/about.py
# Представления для страницы «О проекте»

from django.shortcuts import render


def about(request):
    """Страница 'О проекте'."""
    context = {
        'title': 'О проекте YourTune',
        'description': 'Платформа аффирмаций и ежедневных практик для спокойствия, уверенности и личностного роста.',
    }
    return render(request, 'main/about.html', context)