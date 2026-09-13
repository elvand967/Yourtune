# apps/main/urls.py

from django.urls import path
from . import views  # ← это модуль

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog, name='blog'),
    path('policy/', views.policy, name='policy'),
    path('rules/', views.rules, name='rules'),
]