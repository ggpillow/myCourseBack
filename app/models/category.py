from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course


class Category(Base):
    """
    Модель категории курсов.

    Категория — это справочник для группировки курсов по тематике
    (например, "Программирование", "Дизайн", "Маркетинг"). Используется
    для навигации и фильтрации каталога.

    Категория не может быть удалена, пока в ней есть хотя бы один курс
    (FK с ondelete="RESTRICT" на стороне Course). Это защищает от потери
    данных и нарушения целостности.

    Атрибуты:
        id (int): Первичный ключ, автоинкремент.
        name (str): Название категории. Уникально в рамках системы,
            что исключает дубликаты (например, две "Программирование"
            с разным регистром лучше нормализовать на уровне сервиса).

    Связи (relationships):
        courses (list[Course]): Все курсы, принадлежащие данной категории.
            Один-ко-многим: одна категория содержит много курсов.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    courses: Mapped[list["Course"]] = relationship(back_populates="category")
