# apps/users/utils/avatar.py
# ===========================


import hashlib
import logging
import random
import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL import UnidentifiedImageError

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from unidecode import unidecode


logger = logging.getLogger(__name__)


AVATAR_SIZE = 128
AVATAR_QUALITY = 88


COLOR_PALETTES = [
    ("#1abc9c", "#ffffff"),
    ("#3498db", "#ffffff"),
    ("#9b59b6", "#ffffff"),
    ("#e67e22", "#ffffff"),
    ("#e74c3c", "#ffffff"),
    ("#2c3e50", "#ecf0f1"),
    ("#16a085", "#ffffff"),
    ("#f39c12", "#ffffff"),
    ("#27ae60", "#ffffff"),
    ("#8e44ad", "#ffffff"),
    ("#c0392b", "#ffffff"),
    ("#34495e", "#ecf0f1"),
    ("#d35400", "#ffffff"),
    ("#7f8c8d", "#ffffff"),
    ("#2980b9", "#ffffff"),
    ("#2ecc71", "#ffffff"),
    ("#ff6f61", "#ffffff"),
    ("#6c5ce7", "#ffffff"),
    ("#ff9ff3", "#2d3436"),
    ("#00cec9", "#ffffff"),
    ("#fab1a0", "#2d3436"),
    ("#e84393", "#ffffff"),
    ("#55efc4", "#2d3436"),
    ("#ffeaa7", "#2d3436"),
    ("#fd79a8", "#ffffff"),
    ("#636e72", "#ecf0f1"),
    ("#a29bfe", "#2d3436"),
    ("#00b894", "#ffffff"),
    ("#fdcb6e", "#2d3436"),
    ("#e17055", "#ffffff"),
    ("#0984e3", "#ffffff"),
    ("#dfe6e9", "#2d3436"),
]


def get_user_email(user):
    """
    Возвращает Email пользователя в нормализованном виде.
    """
    return (getattr(user, "email", "") or "").strip().lower()


def normalize_email_for_filename(email):
    """
    Преобразует Email в безопасное ASCII-имя файла.

    Примеры:

    ivan@example.com
    -> ivan_example.com

    иван@example.com
    -> ivan_example.com

    user+music@example.com
    -> user_music_example.com
    """
    email = (email or "").strip().lower()

    transliterated = unidecode(email).lower()

    normalized = re.sub(
        r"[^a-z0-9._@-]+",
        "_",
        transliterated,
    )

    normalized = normalized.replace("@", "_")

    normalized = re.sub(
        r"_+",
        "_",
        normalized,
    ).strip("._-")

    return normalized or "user"


def get_avatar_filename(user):
    """
    Возвращает единое имя JPEG-файла пользователя.
    """
    email = get_user_email(user)
    safe_email = normalize_email_for_filename(email)

    return f"{safe_email}.jpg"


def get_registration_year(user):
    """
    Возвращает год регистрации пользователя.
    """
    date_joined = getattr(user, "date_joined", None)

    if date_joined:
        return date_joined.year

    return timezone.now().year


def avatar_upload_to(instance, filename):
    """
    Возвращает путь относительно MEDIA_ROOT.

    Пример:

    avatars/2026/user_example.com.jpg
    """
    year = get_registration_year(instance.user)
    filename = get_avatar_filename(instance.user)

    return f"avatars/{year}/{filename}"


def random_colors(seed=None):
    """
    Возвращает цветовую пару.

    При наличии seed цвет определяется стабильно.
    Поэтому после повторной генерации у пользователя
    сохраняется тот же цвет фона.
    """
    if not seed:
        return random.choice(COLOR_PALETTES)

    value = int(
        hashlib.sha256(
            seed.encode("utf-8"),
        ).hexdigest(),
        16,
    )

    return COLOR_PALETTES[value % len(COLOR_PALETTES)]


def generate_avatar_text(user):
    """
    Определяет текст для автоматически созданного аватара.

    Приоритет:

    1. Первая буква имени + первая буква фамилии.
    2. Первая буква имени.
    3. Первая буква фамилии.
    4. Две первые буквы локальной части Email.
    5. Первая буква локальной части Email.
    6. Знак вопроса.
    """
    first_name = (
        getattr(user, "first_name", "") or ""
    ).strip()

    last_name = (
        getattr(user, "last_name", "") or ""
    ).strip()

    email = get_user_email(user)

    if first_name and last_name:
        return f"{first_name[0]}{last_name[0]}".upper()

    if first_name:
        return first_name[0].upper()

    if last_name:
        return last_name[0].upper()

    if email:
        local_part = email.split("@", 1)[0]

        if len(local_part) >= 2:
            return local_part[:2].upper()

        return local_part[0].upper()

    return "?"


def get_avatar_font(size):
    """
    Загружает шрифт для автоматической аватарки.

    Шрифт должен быть TrueType/OpenType-файлом с поддержкой
    кириллицы. SCSS-шрифты браузера напрямую использоваться
    Pillow не могут.

    Приоритет:

    1. AVATAR_FONT_PATH из settings;
    2. static/fonts/Inter-Bold.ttf;
    3. static/fonts/DejaVuSans-Bold.ttf.

    Если подходящий файл отсутствует, приложение сообщает
    об ошибке конфигурации вместо использования встроенного
    шрифта Pillow, который не гарантирует поддержку кириллицы.
    """
    font_size = max(int(size * 0.52), 20)

    configured_path = getattr(
        settings,
        "AVATAR_FONT_PATH",
        None,
    )

    candidate_paths = []

    if configured_path:
        candidate_paths.append(
            Path(configured_path),
        )

    base_dir = Path(settings.BASE_DIR)

    candidate_paths.extend(
        [
            base_dir / "static" / "fonts" / "Inter-Bold.ttf",
            base_dir / "static" / "fonts" / "DejaVuSans-Bold.ttf",
        ]
    )

    for font_path in candidate_paths:
        if not font_path.is_file():
            continue

        try:
            return ImageFont.truetype(
                str(font_path),
                font_size,
            )
        except OSError:
            logger.exception(
                "Не удалось загрузить шрифт аватарки: %s",
                font_path,
            )

    raise ImproperlyConfigured(
        "Не найден шрифт для генерации аватарки. "
        "Добавьте Inter-Bold.ttf или DejaVuSans-Bold.ttf "
        "в yourtune/static/fonts/ либо задайте "
        "AVATAR_FONT_PATH в settings."
    )


def generate_avatar_image(user, size=AVATAR_SIZE):
    """
    Генерирует стандартную аватарку пользователя.

    Результат:

    - JPEG;
    - размер size × size;
    - имя файла на основе Email;
    - стабильный цвет фона;
    - точное центрирование букв по видимому bounding box.
    """
    text = generate_avatar_text(user)
    seed = get_user_email(user) or str(user.pk)

    background_color, text_color = random_colors(seed)

    image = Image.new(
        "RGB",
        (size, size),
        background_color,
    )

    draw = ImageDraw.Draw(image)
    font = get_avatar_font(size)

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font,
        anchor="lt",
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = (
        (size - text_width) / 2 - bbox[0],
        (size - text_height) / 2 - bbox[1],
    )

    draw.text(
        position,
        text,
        font=font,
        fill=text_color,
        anchor="lt",
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=AVATAR_QUALITY,
        optimize=True,
        progressive=True,
    )

    return ContentFile(
        buffer.getvalue(),
        name=get_avatar_filename(user),
    )


def validate_image_size(image):
    """
    Проверяет, что у изображения есть корректные размеры.
    """
    width, height = image.size

    if not width or not height:
        raise ValueError(
            "Изображение имеет некорректный размер."
        )


def flatten_transparency(image, user):
    """
    Объединяет прозрачное изображение с цветным фоном.
    """
    if image.mode not in ("RGBA", "LA"):
        return image.convert("RGB")

    image = image.convert("RGBA")

    background_color, _ = random_colors(
        get_user_email(user) or str(user.pk),
    )

    background = Image.new(
        "RGBA",
        image.size,
        background_color,
    )

    background.alpha_composite(image)

    return background.convert("RGB")


def resize_and_crop_center(image, size=AVATAR_SIZE):
    """
    Масштабирует изображение так, чтобы меньшая сторона
    соответствовала требуемому размеру, после чего
    обрезает центральную квадратную область.
    """
    image = image.convert("RGB")
    validate_image_size(image)

    width, height = image.size

    scale = size / min(width, height)

    new_width = max(int(width * scale), size)
    new_height = max(int(height * scale), size)

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    left = (new_width - size) // 2
    top = (new_height - size) // 2

    return image.crop(
        (
            left,
            top,
            left + size,
            top + size,
        )
    )


def process_uploaded_avatar(
    uploaded_file,
    user,
    size=AVATAR_SIZE,):
    """
    Проверяет и преобразует загруженную аватарку.

    На выходе всегда:

    - ContentFile;
    - JPEG;
    - 128x128;
    - безопасное имя на основе Email.
    """
    try:
        uploaded_file.seek(0)

        verification_image = Image.open(uploaded_file)
        verification_image.verify()

        uploaded_file.seek(0)

        image = Image.open(uploaded_file)
        image.load()

        image = flatten_transparency(
            image,
            user,
        )

        image = resize_and_crop_center(
            image,
            size=size,
        )

        buffer = BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=AVATAR_QUALITY,
            optimize=True,
            progressive=True,
        )

        return ContentFile(
            buffer.getvalue(),
            name=get_avatar_filename(user),
        )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        logger.warning(
            "Не удалось обработать аватарку пользователя %s: %s",
            getattr(user, "pk", None),
            exc,
        )

        raise ValueError(
            "Не удалось обработать изображение. "
            "Выберите другой файл."
        ) from exc


def delete_storage_file(file_name):
    """
    Удаляет файл через Django storage.

    Использование storage API позволяет не привязывать
    логику к локальной файловой системе.
    """
    if not file_name:
        return

    try:
        if default_storage.exists(file_name):
            default_storage.delete(file_name)
    except Exception:
        logger.exception(
            "Ошибка удаления файла аватарки: %s",
            file_name,
        )


def delete_avatar_for_profile(profile):
    """
    Удаляет файл, связанный с аватаркой профиля.
    """
    if not profile.avatar:
        return

    delete_storage_file(profile.avatar.name)