from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.like import LikeToggleResponse
from app.services import like_service

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/courses/{course_id}/toggle", response_model=LikeToggleResponse)
async def toggle_like(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await like_service.toggle_like(db, user, course_id)
