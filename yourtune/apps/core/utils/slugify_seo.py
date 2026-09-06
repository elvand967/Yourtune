
# ../apps/core/utils/slugify_seo.py

import re
import uuid

from django.core.cache import cache
from django.utils.text import slugify
from unidecode import unidecode
"""
Генератор SEO - эффективного slug
"""

STOP_WORDS_CACHE_KEY = "core.stop_words"
SEO_REPLACEMENTS_CACHE_KEY = "core.seo_replacements"
CACHE_TTL = 60 * 60


def load_stop_words():
    from apps.core.models.seo import StopWord

    stop_words = {}
    for item in StopWord.objects.values_list("lang", "word"):
        lang, word = item[0], item[1].lower()
        stop_words.setdefault(lang, []).append(word)

    cache.set(STOP_WORDS_CACHE_KEY, stop_words, CACHE_TTL)
    return stop_words


def load_replacements():
    from apps.core.models.seo import SEOReplacement

    replacements = {
        item[0].lower(): item[1].lower()
        for item in SEOReplacement.objects.values_list("source_word", "replacement")
    }

    cache.set(SEO_REPLACEMENTS_CACHE_KEY, replacements, CACHE_TTL)
    return replacements


def get_stop_words():
    value = cache.get(STOP_WORDS_CACHE_KEY)
    return value if value is not None else load_stop_words()


def get_replacements():
    value = cache.get(SEO_REPLACEMENTS_CACHE_KEY)
    return value if value is not None else load_replacements()


def soft_transliterate(text, allow_unicode=False):
    replacements = get_replacements()

    for source_word, replacement in replacements.items():
        pattern = rf"\b{re.escape(source_word)}\b"
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    if allow_unicode:
        return text

    return unidecode(text)


def remove_stop_words(text, stop_langs=("ru", "en")):
    stop_words = get_stop_words()

    for lang in stop_langs:
        words = stop_words.get(lang, [])
        if not words:
            continue

        pattern = r"\b(" + "|".join(map(re.escape, words)) + r")\b"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", text).strip()


def slugify_seo(text, stop_langs=("ru", "en"), max_length=255, allow_unicode=False):
    if not text:
        return str(uuid.uuid4())[:8]

    text = text.lower().strip()
    text = remove_stop_words(text, stop_langs=stop_langs)
    text = soft_transliterate(text, allow_unicode=allow_unicode)

    slug = slugify(text, allow_unicode=allow_unicode)
    return slug[:max_length]