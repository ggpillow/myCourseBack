from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AlreadyExistsError,
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud import user as crud
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.services.email_service import send_welcome_email


def _issue_tokens(user: User) -> Token:
    sub = str(user.id)
    return Token(
        access_token=create_access_token(sub),
        refresh_token=create_refresh_token(sub),
    )


async def register(db: AsyncSession, user_in: UserCreate) -> User:
    if await crud.get_by_email(db, user_in.email) is not None:
        raise AlreadyExistsError("Пользователь с таким email уже существует")
    user = await crud.create(db, user_in)

    # Приветственное письмо (заглушка)
    await send_welcome_email(user.email, user.full_name)

    return user


async def login(db: AsyncSession, email: str, password: str) -> Token:
    user = await crud.get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Неверный email или пароль")
    return _issue_tokens(user)


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> Token:
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise UnauthorizedError("Невалидный refresh-токен")

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as err:
        raise UnauthorizedError("Невалидный refresh-токен") from err

    user = await crud.get_by_id(db, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")

    return _issue_tokens(user)


async def change_password(
    db: AsyncSession,
    user: User,
    old_password: str,
    new_password: str,
) -> None:
    if not verify_password(old_password, user.hashed_password):
        raise BadRequestError("Неверный старый пароль")
    if old_password == new_password:
        raise BadRequestError("Новый пароль должен отличаться от старого")
    await crud.change_password(db, user, new_password)
