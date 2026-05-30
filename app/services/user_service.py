from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.crud import user as crud
from app.models.user import User
from app.schemas.user import UserUpdate


async def get_or_404(db: AsyncSession, user_id: int) -> User:
    """Вернуть пользователя по id или 404."""
    user = await crud.get_by_id(db, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return user


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    """Обновить профиль текущего пользователя."""
    return await crud.update(db, user, data)
