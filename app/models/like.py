from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Like(Base):
    """
    Модель лайка курса пользователем.

    Связующая сущность между User и Course, фиксирующая факт того, что
    пользователь отметил курс как понравившийся. Используется как
    социальная механика: рейтинг популярности курсов, рекомендации,
    показатель востребованности контента.

    Уникальность пары (user_id, course_id) на уровне БД гарантирует, что
    один пользователь может поставить лайк курсу только один раз. Повторный
    клик по кнопке "Нравится" должен снимать лайк (удалять запись), а не
    создавать дубликат — это типичная toggle-механика.

    При удалении пользователя или курса соответствующие лайки удаляются
    каскадно (ondelete="CASCADE"), что исключает появление "висящих"
    записей в БД.

    Атрибуты:
        id (int): Первичный ключ, автоинкремент.
        user_id (int): FK на пользователя, поставившего лайк.
            Проиндексирован для быстрого получения списка лайкнутых
            курсов пользователя.
        course_id (int): FK на лайкнутый курс. Проиндексирован для
            быстрого подсчёта количества лайков курса.
        created_at (datetime): Дата и время постановки лайка с TZ.
            Устанавливается на стороне БД.

    Связи (relationships):
        user (User): Пользователь, поставивший лайк. Многие-к-одному.
        course (Course): Лайкнутый курс. Многие-к-одному.

    Ограничения:
        uq_like_user_course: Пара (user_id, course_id) уникальна —
            один пользователь лайкает один курс только один раз.
    """
    
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_like_user_course"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="likes")
    course: Mapped["Course"] = relationship(back_populates="likes")
