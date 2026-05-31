"""
Пакет ORM-моделей приложения.

Импортирует и реэкспортирует все модели и Enum-классы, чтобы:
1. Зарегистрировать модели в Base.metadata — необходимо для корректной
   работы Alembic (автогенерация миграций видит все таблицы).
2. Предоставить единую точку импорта: `from app.models import User, Course`
   вместо длинных путей к каждому файлу.
"""

from app.models.category import Category
from app.models.course import Course
from app.models.like import Like
from app.models.purchase import Purchase
from app.models.topic import Topic
from app.models.user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "Category",
    "Course",
    "Topic",
    "Purchase",
    "Like",
]
