from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.like import Like
    from app.models.purchase import Purchase
    from app.models.topic import Topic


class Course(Base):
    """
    Модель курса — центральная сущность платформы микрообучения.

    Курс представляет собой учебный продукт, состоящий из упорядоченного
    набора коротких тем (Topic). Курс принадлежит одной категории, может
    быть куплен пользователями и получать лайки.

    Концепция микрообучения реализована через темы: каждая тема — это
    небольшой самостоятельный учебный фрагмент. Часть тем может быть
    бесплатной (is_free=True) для демонстрации содержания курса до покупки.

    Атрибуты:
        id (int): Первичный ключ, автоинкремент.
        title (str): Название курса (до 255 символов).
        description (str): Подробное описание курса. Может быть пустой
            строкой по умолчанию. Ограничение — 2000 символов.
        price (int): Цена курса в минимальных денежных единицах (копейках).
            Хранится как целое число для исключения ошибок округления,
            свойственных типу float. Значение 0 означает бесплатный курс.
        category_id (int): FK на категорию. Запрещено удаление категории
            при наличии связанных курсов (ondelete="RESTRICT").
            Проиндексирован для быстрой фильтрации по категории.
        created_at (datetime): Дата и время создания курса с TZ.
            Устанавливается на стороне БД.

    Связи (relationships):
        category (Category): Категория, к которой принадлежит курс.
            Многие-к-одному.
        topics (list[Topic]): Темы курса, отсортированные по order_index.
            Удаляются каскадно вместе с курсом. Один-ко-многим.
        purchases (list[Purchase]): Все покупки данного курса разными
            пользователями. Удаляются каскадно. Один-ко-многим.
        likes (list[Like]): Все лайки данного курса. Удаляются каскадно.
            Один-ко-многим.
    """

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    price: Mapped[int] = mapped_column(nullable=False, default=0)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    category: Mapped["Category"] = relationship(back_populates="courses")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Topic.order_index",
    )
    purchases: Mapped[list["Purchase"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
