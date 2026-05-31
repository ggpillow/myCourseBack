from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.like import Like
    from app.models.purchase import Purchase


class UserRole(str, Enum):
    """
    Роли пользователей в системе.

    Используется как для бизнес-логики (разграничение прав доступа),
    так и для хранения в БД в виде нативного PostgreSQL ENUM-типа "user_role".

    Наследование от str позволяет сравнивать роль напрямую со строкой
    и сериализовать в JSON без дополнительных преобразований.

    Значения:
        USER: Обычный пользователь платформы (студент). Может просматривать
            бесплатные темы, покупать курсы, ставить лайки.
        ADMIN: Администратор. Имеет полный доступ к управлению
            курсами, категориями, темами и пользователями.
    """

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    Модель пользователя платформы микрообучения.

    Представляет учётную запись пользователя — студента или администратора.
    Является корневой сущностью для покупок и лайков: при удалении пользователя
    каскадно удаляются все его покупки и лайки.

    Атрибуты:
        id (int): Первичный ключ, автоинкремент.
        email (str): Email пользователя. Уникален в рамках всей системы,
            используется как логин при аутентификации. Проиндексирован
            для быстрого поиска при входе.
        hashed_password (str): Хэш пароля (bcrypt). В чистом виде пароль
            нигде не хранится и не логируется.
        full_name (str): Полное имя пользователя. Может быть пустой строкой
            (если пользователь не заполнил профиль).
        role (UserRole): Роль пользователя. По умолчанию — USER.
            Хранится в БД как нативный PostgreSQL ENUM-тип "user_role".
        created_at (datetime): Дата и время регистрации с учётом часового
            пояса. Устанавливается на стороне БД (server_default).

    Связи (relationships):
        purchases (list[Purchase]): Все курсы, купленные пользователем.
            При удалении пользователя покупки удаляются каскадно.
        likes (list[Like]): Все лайки, поставленные пользователем курсам.
            При удалении пользователя лайки удаляются каскадно.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
        default=UserRole.USER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    purchases: Mapped[list["Purchase"]] = relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
    )