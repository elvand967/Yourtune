# apps/core/templatetags/footer_menu.py
# =====================================

from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_footer_menu():
    """
    Рендерит HTML подвала с меню и кнопкой «Наверх».
    """
    menu_items = [
        {
            "label": "Темы",
            "url": "#topics",
        },
        {
            "label": "Подборки",
            "url": "#featured",
        },
        {
            "label": "Практика дня",
            "url": "#daily",
        },
        {
            "label": "Статьи",
            "url": "#blog",
        },
        {
            "label": "Политика",
            "url_name": "legal:policy",
        },
        {
            "label": "Правила",
            "url_name": "legal:rules",
        },
    ]

    links_html = ""

    for item in menu_items:
        url = _resolve_url(item)

        if not url:
            continue

        links_html += (
            f'<a class="site-footer__link footer-link" '
            f'href="{url}">{item["label"]}</a>'
        )

    html = (
        '<div class="site-footer__inner">\n'
        '  <div class="site-footer__top">\n'
        '    <section class="site-footer__brand footer-reveal" '
        'aria-labelledby="footer-brand-title">\n'
        '      <h2 id="footer-brand-title" class="site-footer__title">YourTune</h2>\n'
        '      <p class="site-footer__description">\n'
        '        Аффирмации, ежедневные практики и тематические подборки\n'
        '        для спокойствия, уверенности и внутренней опоры.\n'
        '      </p>\n'
        '    </section>\n'
        '    <nav class="site-footer__links footer-reveal" '
        'aria-label="Навигация в подвале">\n'
        f'      {links_html}\n'
        '    </nav>\n'
        '  </div>\n'
        '  <div class="site-footer__bottom footer-reveal">\n'
        '    <span>YourTune &copy; 2026</span>\n'
        '    <button\n'
        '      type="button"\n'
        '      class="footer-back-to-top"\n'
        '      id="backToTop"\n'
        '      aria-label="Вернуться наверх"\n'
        '    >\n'
        '      &uarr;\n'
        '    </button>\n'
        '  </div>\n'
        '</div>'
    )

    return mark_safe(html)


def _resolve_url(item):
    """
    Возвращает URL для пункта футера.

    Поддерживает прямые ссылки и именованные маршруты.
    """
    if item.get("url"):
        return item["url"]

    url_name = item.get("url_name")

    if not url_name:
        return ""

    try:
        return reverse(url_name)
    except NoReverseMatch:
        return ""