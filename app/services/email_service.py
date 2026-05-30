from app.core.logging import logger


async def send_purchase_confirmation(
    user_email: str,
    user_name: str,
    course_title: str,
    course_price: float,
) -> None:
    """
    Заглушка отправки email-уведомления о покупке курса.
    В реальном проекте здесь была бы интеграция с SMTP / SendGrid / Mailgun.
    """
    logger.info(
        f"📧 [EMAIL STUB] Отправлено письмо на {user_email}:\n"
        f"   Тема: Подтверждение покупки курса\n"
        f"   Привет, {user_name}!\n"
        f"   Вы успешно приобрели курс «{course_title}» за {course_price} ₽.\n"
        f"   Спасибо за покупку! 🎓"
    )


async def send_welcome_email(user_email: str, user_name: str) -> None:
    """Заглушка приветственного письма после регистрации."""
    logger.info(
        f"📧 [EMAIL STUB] Отправлено письмо на {user_email}:\n"
        f"   Тема: Добро пожаловать!\n"
        f"   Привет, {user_name}! Рады видеть тебя на нашей платформе. 👋"
    )
