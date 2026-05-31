from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Purchase(Base):
    """
    Модель покупки курса пользователем.

    Связующая сущность между User и Course, фиксирующая факт приобретения
    курса конкретным пользователем. Наличие записи в этой таблице даёт
    пользователю доступ к платному содержимому курса (всем темам, включая
    те, у которых is_free=False).

    Уникальность пары (user_id, course_id) на уровне БД гарантирует, что
    один пользователь не может купить один и тот же курс дважды. Защита
    работает даже при гонке параллельных HTTP-запросов, поскольку
    реализована на уровне СУБД, а не приложения.

    При удалении пользователя или курса соответствующие покупки удаляются
    каскадно (ondelete="CASCADE").

    Атрибуты:
        id (int): Первичный ключ, автоинкремент.
        user_id (int): FK на пользователя, совершившего покупку.
            Проиндексирован для быстрого получения списка покупок юзера.
        course_id (int): FK на купленный курс. Проиндексирован для
            быстрого подсчёта покупок курса.
        created_at (datetime): Дата и время совершения покупки с TZ.
            Устанавливается на стороне БД, что исключает рассинхронизацию
            времени между инстансами приложения.

    Связи (relationships):
        user (User): Пользователь, совершивший покупку. Многие-к-одному.
        course (Course): Купленный курс. Многие-к-одному.

    Ограничения:
        uq_purchase_user_course: Пара (user_id, course_id) уникальна —
            один пользователь покупает один курс только один раз.
    """

    __tablename__ = "purchases"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_purchase_user_course"),)

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

    user: Mapped["User"] = relationship(back_populates="purchases")
    course: Mapped["Course"] = relationship(back_populates="purchases")
