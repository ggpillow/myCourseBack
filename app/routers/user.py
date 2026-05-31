"""
Роутер пользователей.

Эндпоинты:
- GET   /users/me        — профиль текущего пользователя.
- PATCH /users/me        — обновление профиля (имя, email).
- GET   /users/{user_id} — публичный профиль пользователя по id.

Смена пароля вынесена в роутер аутентификации (/auth/change-password) —
там она рядом с остальными операциями над учётными данными.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Профиль текущего пользователя."""
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновление профиля текущего пользователя."""
    return await user_service.update_profile(db, current_user, data)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Публичный профиль пользователя по id."""
    return await user_service.get_or_404(db, user_id)