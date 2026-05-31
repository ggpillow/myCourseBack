"""
Роутер аутентификации.

Эндпоинты:
- POST /auth/register — регистрация нового пользователя.
- POST /auth/login — выдача access + refresh токенов (OAuth2-форма: username=email, password).
- POST /auth/refresh — обновление пары токенов по refresh-токену.
- POST /auth/change-password — смена пароля авторизованного пользователя.

На register и login применён rate limit для защиты от спама регистраций
и брутфорса паролей.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    PasswordChange,
    RefreshRequest,
    Token,
)
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.register(db, payload)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2-совместимый логин.
    В Swagger: username = email пользователя, password = пароль.
    """
    return await auth_service.login(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.refresh_tokens(db, payload.refresh_token)

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await auth_service.change_password(
        db, current_user, payload.old_password, payload.new_password
    )
    return None