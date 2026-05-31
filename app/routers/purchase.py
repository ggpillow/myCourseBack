"""
Роутер покупок курсов.

Эндпоинты:
- GET  /purchases/my                  — список курсов, купленных текущим юзером.
- POST /purchases/courses/{course_id} — оформление покупки курса.

Оба эндпоинта требуют авторизации. Реальной оплаты нет — для учебного
проекта факт покупки эмулируется созданием записи Purchase.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.purchase import PurchaseRead
from app.services import purchase_service
from fastapi import Query

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/my", response_model=list[PurchaseRead])
async def my_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await purchase_service.list_my_purchases(db, user, skip=skip, limit=limit)


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