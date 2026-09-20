# apps/users/utils/avatar.py

import os
import hashlib
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings

# Палитра разработок
COLOR_PALETTES = [
        ("#1abc9c", "#ffffff"),  # бирюза + белый
        ("#3498db", "#ffffff"),  # синий + белый
        ("#9b59b6", "#ffffff"),  # фиолетовый + белый
        ("#e67e22", "#ffffff"),  # оранжевый + белый
        ("#e74c3c", "#ffffff"),  # красный + белый
        ("#2c3e50", "#ecf0f1"),  # тёмно-синий + светло-серый
        ("#16a085", "#ffffff"),  # тёмная бирюза + белый
        ("#f39c12", "#ffffff"),  # жёлто-оранжевый + белый
        ("#27ae60", "#ffffff"),  # зелёный + белый
        ("#8e44ad", "#ffffff"),  # насыщенный фиолетовый + белый
        ("#c0392b", "#ffffff"),  # бордовый + белый
        ("#34495e", "#ecf0f1"),  # графитовый + светло-серый
        ("#d35400", "#ffffff"),  # ярко-оранжевый + белый
        ("#7f8c8d", "#ffffff"),  # серо-бирюзовый + белый
        ("#2980b9", "#ffffff"),  # ярко-синий + белый
        ("#2ecc71", "#ffffff"),  # ярко-зелёный + белый
        ("#ff6f61", "#ffffff"),  # коралловый + белый
        ("#6c5ce7", "#ffffff"),  # индиго + белый
        ("#ff9ff3", "#2d3436"),  # розовый пастель + графит
        ("#00cec9", "#ffffff"),  # яркая бирюза + белый
        ("#fab1a0", "#2d3436"),  # персиковый + графит
        ("#e84393", "#ffffff"),  # ярко-розовый + белый
        ("#55efc4", "#2d3436"),  # мятный + графит
        ("#ffeaa7", "#2d3436"),  # мягкий жёлтый + графит
        ("#fd79a8", "#ffffff"),  # малиновый + белый
        ("#636e72", "#ecf0f1"),  # тёмно-серый + светло-серый
        ("#a29bfe", "#2d3436"),  # нежно-фиолетовый + графит
        ("#00b894", "#ffffff"),  # морская волна + белый
        ("#fdcb6e", "#2d3436"),  # янтарный + графит
        ("#e17055", "#ffffff"),  # терракотовый + белый
        ("#0984e3", "#ffffff"),  # ярко-голубой + белый
        ("#dfe6e9", "#2d3436"),  # светло-серый + графит
]


def dynamic_avatar_path(instance, filename):
    """
    Путь: avatars/slug-org/email-prefix_YYMMDD.jpg
    Если нет организации: avatars/personal/year/month/email-prefix_YYMMDD.jpg
    """
    # Защита на случай, если email не заполнен (редкий кейс для соцсетей)
    email = getattr(instance.user, 'email', '') or f"user_{instance.user.id}@local"
    user_prefix = email.split('@')[0]

    # Защита на случай, если created_at еще не сохранен в БД
    created_at = getattr(instance.user, 'created_at', None) or timezone.now()
    date_str = created_at.strftime('%y%m%d')

    filename = f"{user_prefix}_{date_str}.jpg"

    if getattr(instance, 'organization', None):
        return os.path.join("avatars", instance.organization.slug, filename)

    date = timezone.now()
    return os.path.join("avatars", "personal", str(date.year), f"{date.month:02d}", filename)


def generate_avatar_text(user):
    first = getattr(user, "first_name", "")
    last = getattr(user, "last_name", "")
    if first and last:
        return f"{first[0].upper()}{last[0].upper()}"
    email = getattr(user, "email", "")
    return email[0].upper() if email else "?"


def generate_avatar_image(user, size=128):
    """РЕЖИМ 1: Генерация буквенной заглушки (для Email-регистраций или сбоев соцсетей)"""
    text = generate_avatar_text(user)
    email = getattr(user, "email", "") or str(user.pk)

    idx = int(hashlib.sha256(email.encode()).hexdigest(), 16)
    bg_color, text_color = COLOR_PALETTES[idx % len(COLOR_PALETTES)]

    img = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    font_path = Path(settings.BASE_DIR) / "apps" / "core" / "static" / "core" / "fonts" / "DejaVuSans-Bold.ttf"
    font_size = int(size * 0.5)

    try:
        font = ImageFont.truetype(str(font_path), font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2, (size - h) / 2 - h * 0.25), text, font=font, fill=text_color)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return ContentFile(buffer.getvalue(), name="avatar.jpg")


def resize_and_crop_center(img, size=128):
    """Вспомогательная функция: идеальный квадратный кроп по центру и ресайз"""
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    width, height = img.size
    min_side = min(width, height)
    left = (width - min_side) / 2
    top = (height - min_side) / 2
    img = img.crop((left, top, left + min_side, top + min_side))

    return img.resize((size, size), Image.LANCZOS)


def process_uploaded_avatar(file, size=128):
    """РЕЖИМ 2: Принудительный кроп и ресайз загруженного пользователем файла в память"""
    try:
        img = Image.open(file)
        img = resize_and_crop_center(img, size)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return ContentFile(buffer.getvalue())
    except Exception as e:
        print(f"Ошибка обработки загруженного изображения: {e}")
        return file


def process_avatar_from_url(url, size=128):
    """РЕЖИМ 3: Скачивание аватарки из соцсетей с последующей обработкой в JPEG"""
    try:
        # Скачиваем картинку с таймаутом, чтобы не вешать поток сервера
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Читаем байты в Pillow
            img = Image.open(BytesIO(response.content))
            img = resize_and_crop_center(img, size)

            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            return ContentFile(buffer.getvalue())
    except Exception as e:
        print(f"Ошибка скачивания или обработки аватара по URL: {e}")

    # Если скачать не удалось, возвращаем None, чтобы сработал резервный Режим 1
    return None


def delete_old_avatar(path):
    if path:
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(full_path):
            os.remove(full_path)


avatar_upload_to = dynamic_avatar_path
