from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase import Purchase


async def get_by_id(session: AsyncSession, purchase_id: int) -> Purchase | None:
    """Получение покупки по id."""
    return await session.get(Purchase, purchase_id)


async def get_by_user_and_course(
    session: AsyncSession, user_id: int, course_id: int
) -> Purchase | None:
    """
    Проверка, купил ли пользователь конкретный курс.
    Используется для:
    - проверки доступа к контенту курса
    - предотвращения повторной покупки
    """
    result = await session.execute(
        select(Purchase).where(
            Purchase.user_id == user_id,
            Purchase.course_id == course_id,
        )
    )
    return result.scalar_one_or_none()


async def get_by_user(session: AsyncSession, user_id: int) -> list[Purchase]:
    """Все покупки пользователя со связанными курсами (для 'мои курсы')."""
    result = await session.execute(
        select(Purchase)
        .options(selectinload(Purchase.course))
        .where(Purchase.user_id == user_id)
        .order_by(Purchase.id.desc())
    )
    return list(result.scalars().all())


async def create(session: AsyncSession, user_id: int, course_id: int) -> Purchase:
    """Создание записи о покупке курса."""
    purchase = Purchase(user_id=user_id, course_id=course_id)
    session.add(purchase)
    await session.commit()
    await session.refresh(purchase)
    return purchase


async def exists(session: AsyncSession, user_id: int, course_id: int) -> bool:
    """Быстрая проверка факта покупки (true/false)."""
    purchase = await get_by_user_and_course(session, user_id, course_id)
    return purchase is not None
