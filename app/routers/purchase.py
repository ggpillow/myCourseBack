from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.purchase import PurchaseRead
from app.services import purchase_service

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/my", response_model=list[PurchaseRead])
async def my_purchases(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await purchase_service.list_my_purchases(db, user)


@router.post(
    "/courses/{course_id}",
    response_model=PurchaseRead,
    status_code=status.HTTP_201_CREATED,
)
async def buy_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await purchase_service.purchase_course(db, user, course_id)
