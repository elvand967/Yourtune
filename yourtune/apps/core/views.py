# apps/core/views.py

from django.shortcuts import render


def about(request):
    """Страница 'О проекте'."""
    return render(request, 'core/about.html')


def faq(request):
    """Страница 'FAQ'."""
    return render(request, 'core/faq.html')