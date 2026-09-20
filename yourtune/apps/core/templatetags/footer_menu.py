# apps/core/templatetags/footer_menu.py
# Templatetag для рендеринга меню подвала

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_footer_menu():
    """
    Рендерит HTML подвала с меню и кнопкой "Наверх".
    Возвращает безопасный HTML для вставки в шаблон.
    """
    menu_items = [
        {'label': 'Темы', 'url': '#topics'},
        {'label': 'Подборки', 'url': '#featured'},
        {'label': 'Практика дня', 'url': '#daily'},
        {'label': 'Статьи', 'url': '#blog'},
    ]

    # Генерируем HTML ссылок
    links_html = ''.join([
        f'<a class="site-footer__link footer-link" href="{item["url"]}">{item["label"]}</a>'
        for item in menu_items
    ])

    # Полный HTML подвала
    html = (
        '<div class="site-footer__inner">\n'
        '  <div class="site-footer__top">\n'
        '    <section class="site-footer__brand footer-reveal" aria-labelledby="footer-brand-title">\n'
        '      <h2 id="footer-brand-title" class="site-footer__title">YourTune</h2>\n'
        '      <p class="site-footer__description">\n'
        '        Аффирмации, ежедневные практики и тематические подборки\n'
        '        для спокойствия, уверенности и внутренней опоры.\n'
        '      </p>\n'
        '    </section>\n'
        '    <nav class="site-footer__links footer-reveal" aria-label="Навигация в подвале">\n'
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