
# apps/account/utils/email_utils.py

import random
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

def generate_email_code():
    # Генерируем код подтверждения в формате XX-XXX, например 42-837
    part1 = random.randint(10, 99)
    part2 = random.randint(100, 999)
    return f"{part1}-{part2}"

def send_email_confirmation_code(user):
    # Генерируем код для пользователя
    code = generate_email_code()

    # Сохраняем код и дату генерации в профиль пользователя
    profile = user.profile
    profile.email_code = code
    profile.email_code_created = timezone.now()
    profile.save()

    subject = "Код подтверждения регистрации на Moloshop.by"

    # Передаем в шаблон код, email и имя пользователя
    context = {
        "code": code,
        "user_email": user.email,
        "first_name": user.first_name,  # для условного приветствия в письме
    }

    # Рендерим html формат письма с контекстом
    html_content = render_to_string("account/components/confirmation_email.html", context)

    # Создаем email с альтернативным HTML содержимым
    msg = EmailMultiAlternatives(
        subject=subject,
        body=f"Ваш код подтверждения: {code}",  # Текстовая версия (для почтовых клиентов без поддержки HTML)
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)