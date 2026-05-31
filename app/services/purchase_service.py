"""
Сервис покупок курсов.

Отвечает за:
- оформление покупки с проверкой существования курса и запретом
  на повторную покупку (один пользователь — одна покупка курса);
- отправку email-подтверждения после успешной покупки;
- получение списка купленных пользователем курсов для раздела
  "мои курсы".

Денежные операции здесь не выполняются — оплата эмулируется самим
фактом создания записи Purchase (для учебного проекта). При интеграции
с платёжным шлюзом этот сервис станет точкой подключения.
"""

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

    await send_purchase_confirmation(
        user_email=user.email,
        user_name=user.full_name,
        course_title=course.title,
        course_price=float(course.price),
    )

    return purchase


async def list_my_purchases(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 50,
) -> list[Purchase]:
    return await crud.get_by_user(db, user.id, skip=skip, limit=limit)