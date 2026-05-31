from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course


class Topic(Base):
    """
    Модель темы (учебной единицы) внутри курса.

    Тема — это атомарный учебный фрагмент в рамках микрообучения:
    короткий самостоятельный материал, который пользователь может изучить
    за одну сессию. Каждая тема принадлежит ровно одному курсу и имеет
    свой порядковый номер в нём.

    Бесплатные темы (is_free=True) доступны всем пользователям без покупки
    курса — это позволяет реализовать механику "превью" для привлечения
    покупателей. Платные темы доступны только тем, кто приобрёл курс.

    Уникальность пары (course_id, order_index) на уровне БД гарантирует,
    что в одном курсе не может быть двух тем с одинаковым порядковым
    номером.

    Атрибуты:
        id (int): Первичный ключ, автоинкремент.
        title (str): Заголовок темы (до 255 символов).
        content (str): Текстовое содержание темы. Тип Text без ограничения
            длины — для размещения полноценного учебного материала
            (статьи, конспекта, инструкции).
        order_index (int): Порядковый номер темы в курсе. По умолчанию 1.
            Используется для сортировки тем при отображении курса.
        is_free (bool): Флаг бесплатного доступа. Если True — тема
            доступна всем пользователям без покупки курса.
        course_id (int): FK на курс. При удалении курса все его темы
            удаляются каскадно. Проиндексирован для быстрой выборки
            тем конкретного курса.

    Связи (relationships):
        course (Course): Курс, к которому принадлежит тема. Многие-к-одному.

    Ограничения:
        uq_topic_course_order: Пара (course_id, order_index) уникальна —
            нельзя создать две темы с одинаковым порядковым номером
            в одном курсе.
    """

    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("course_id", "order_index", name="uq_topic_course_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    order_index: Mapped[int] = mapped_column(nullable=False, default=1)
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    course: Mapped["Course"] = relationship(back_populates="topics")
