# apps/core/templatetags/footer_menu.py

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def render_footer_menu(context):
    """
    Выводит внутреннюю разметку footer.

    Внешний элемент:

        <footer class="site-footer">

    находится в base.html, поэтому этот тег выводит только
    внутреннее содержимое footer.
    """

    return """
    <div class="site-footer__inner">

        <div class="site-footer__top">

            <section
                class="site-footer__brand footer-reveal"
                aria-labelledby="footer-brand-title"
            >
                <h2
                    id="footer-brand-title"
                    class="site-footer__title"
                >
                    YourTune
                </h2>

                <p class="site-footer__description">
                    Аффирмации, ежедневные практики и тематические подборки
                    для спокойствия, уверенности и внутренней опоры.
                </p>
            </section>

            <nav
                class="site-footer__links footer-reveal"
                aria-label="Навигация в подвале"
            >
                <a
                    class="site-footer__link footer-link"
                    href="#topics"
                >
                    Темы
                </a>

                <a
                    class="site-footer__link footer-link"
                    href="#featured"
                >
                    Подборки
                </a>

                <a
                    class="site-footer__link footer-link"
                    href="#daily"
                >
                    Практика дня
                </a>

                <a
                    class="site-footer__link footer-link"
                    href="#blog"
                >
                    Статьи
                </a>
            </nav>

        </div>

        <div class="site-footer__bottom footer-reveal">

            <span>
                YourTune © 2026
            </span>

            <button
                type="button"
                class="footer-back-to-top"
                aria-label="Вернуться наверх"
                aria-hidden="true"
                tabindex="-1"
            >
                <span aria-hidden="true">↑</span>
            </button>

        </div>

    </div>
    """