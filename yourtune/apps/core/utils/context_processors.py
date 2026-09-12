
# apps/core/context_processors.py

from django.templatetags.static import static


def site_defaults(request):
    """
    Глобальные SEO- и брендовые значения для шаблонов.
    """

    og_image_url = request.build_absolute_uri(
        static("core/img/og-default.jpg")
    )

    return {
        "site_name": "YourTune",
        "site_default_title": (
            "YourTune — аффирмации и ежедневные практики"
        ),
        "site_default_description": (
            "YourTune — платформа аффирмаций, тематических подборок, "
            "ежедневных практик и статей для спокойствия, уверенности "
            "и личностного роста."
        ),
        "site_default_og_image": og_image_url,
    }