# apps/main/views.py

from django.shortcuts import render


def home(request):
    context = {
        "hero": {
            "badge": "Один сайт — три настроения",
            "title": "Подборки аффирмаций на каждый день",
            "description": (
                "Мягкие практики для спокойствия, уверенности "
                "и внутренней опоры."
            ),
            "primary_action": {
                "label": "Смотреть темы",
                "anchor": "#topics",
            },
            "secondary_action": {
                "label": "Популярные подборки",
                "anchor": "#featured",
            },
        },

        "stats": [
            {
                "value": "10",
                "label": "ключевых тем аффирмаций",
            },
            {
                "value": "365",
                "label": "ежедневных практик",
            },
            {
                "value": "3",
                "label": "настроения оформления",
            },
        ],

        "topics": [
            {
                "title": "Уверенность в себе",
                "style": "violet",
                "anchor": "#featured",
            },
            {
                "title": "Изобилие и процветание",
                "style": "blue",
                "anchor": "#featured",
            },
            {
                "title": "Здоровье и благополучие",
                "style": "rose",
                "anchor": "#featured",
            },
            {
                "title": "Любовь и отношения",
                "style": "green",
                "anchor": "#featured",
            },
            {
                "title": "Стресс и тревога",
                "style": "yellow",
                "anchor": "#daily",
            },
            {
                "title": "Личностный рост",
                "style": "blue",
                "anchor": "#blog",
            },
        ],

        "featured_collections": [
            {
                "title": "Аффирмации на уверенность",
                "description": (
                    "Поддержка самооценки и внутренней устойчивости"
                ),
                "count": "12",
                "style": "violet",
            },
            {
                "title": "Аффирмации на изобилие",
                "description": (
                    "Фокус на достатке, открытости и благополучии"
                ),
                "count": "18",
                "style": "blue",
            },
            {
                "title": "Аффирмации на спокойствие",
                "description": (
                    "Мягкое снижение тревожности и напряжения"
                ),
                "count": "9",
                "style": "green",
            },
        ],

        "daily_focus": {
            "title": "Ежедневный фокус",
            "description": (
                "Небольшая практика для возвращения к себе"
            ),
            "label": (
                "Сегодня выбираю спокойствие, ясность "
                "и внутреннюю опору"
            ),
            "bars": [
                {
                    "style": "violet",
                    "width": 86,
                },
                {
                    "style": "yellow",
                    "width": 72,
                },
                {
                    "style": "rose",
                    "width": 64,
                },
                {
                    "style": "blue",
                    "width": 48,
                },
            ],
        },

        "articles": [
            {
                "style": "violet",
                "title": "Как использовать аффирмации каждый день",
            },
            {
                "style": "blue",
                "title": "Практика возвращения к спокойствию",
            },
            {
                "style": "rose",
                "title": "Как сформировать внутреннюю опору",
            },
            {
                "style": "green",
                "title": "Небольшие ритуалы заботы о себе",
            },
        ],

        "cta": {
            "title": "Начни практику сегодня",
            "description": (
                "Сохраняй любимые подборки, возвращайся к ним "
                "утром и вечером и постепенно выстраивай личную "
                "систему внутренней поддержки."
            ),
            "primary_action": {
                "label": "Перейти к подборкам",
                "anchor": "#topics",
            },
            "secondary_action": {
                "label": "Читать статьи",
                "anchor": "#blog",
            },
        },
    }

    return render(
        request,
        "main/home.html",
        context,
    )