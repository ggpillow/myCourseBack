# app/services/like_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import like as crud
from app.models.user import User
from app.schemas.like import LikeToggleResponse
from app.services import course_service


async def toggle_like(db: AsyncSession, user: User, course_id: int) -> LikeToggleResponse:
    """Переключает лайк на курсе."""
    await course_service.get_or_404(db, course_id)

    is_liked, likes_count = await crud.toggle(db, user.id, course_id)

    return LikeToggleResponse(
        course_id=course_id,
        is_liked=is_liked,
        likes_count=likes_count,
    )
