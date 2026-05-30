from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError
from app.crud import purchase as crud
from app.models.purchase import Purchase
from app.models.user import User
from app.services import course_service
from app.services.email_service import send_purchase_confirmation


async def purchase_course(db: AsyncSession, user: User, course_id: int) -> Purchase:
    course = await course_service.get_or_404(db, course_id)
    if await crud.exists(db, user.id, course_id):
        raise AlreadyExistsError("Курс уже куплен")
    purchase = await crud.create(db, user.id, course_id)

    # Email-уведомление (заглушка)
    await send_purchase_confirmation(
        user_email=user.email,
        user_name=user.full_name,
        course_title=course.title,
        course_price=float(course.price),
    )

    return purchase


async def list_my_purchases(db: AsyncSession, user: User) -> list[Purchase]:
    return await crud.get_by_user(db, user.id)
