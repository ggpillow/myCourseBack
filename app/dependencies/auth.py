from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_token
from app.crud import user as crud
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
# Опциональная схема — не кидает 401, если токена нет
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

_credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Невалидные учётные данные",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    """
    Достаёт текущего пользователя из access-токена.
    Кидает 401, если токен битый, не access или юзер удалён.
    """
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise _credentials_exc

    sub = payload.get("sub")
    if sub is None:
        raise _credentials_exc
    try:
        user_id = int(sub)
    except (ValueError, TypeError) as err:
        raise _credentials_exc from err

    user = await crud.get_by_id(db, user_id)
    if user is None:
        raise _credentials_exc

    return user


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_session),
) -> User | None:
    """
    Возвращает пользователя, если есть валидный токен.
    Если токена нет или он битый — возвращает None (без ошибки).
    Используется в эндпоинтах, которые работают и для гостей, и для авторизованных.
    """
    if token is None:
        return None

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None

    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        return None

    return await crud.get_by_id(db, user_id)


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Требует, чтобы текущий пользователь был админом.
    Кидает 403, если прав не хватает.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user


# Алиас: новые роутеры используют имя require_admin
require_admin = get_current_admin
