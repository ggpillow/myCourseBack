"""
CRUD-операции для пользователей.

Особенность: пароль хэшируется внутри create/change_password — это
гарантирует, что в БД никогда не попадёт пароль в открытом виде,
даже если вызывающий код забудет про хэширование.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create(session: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update(session: AsyncSession, user: User, user_in: UserUpdate) -> User:
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    await session.commit()
    await session.refresh(user)
    return user


async def change_password(session: AsyncSession, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    await session.commit()
    await session.refresh(user)
    return user
