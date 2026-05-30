from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Like


async def get_by_user_and_course(
    session: AsyncSession, user_id: int, course_id: int
) -> Like | None:
    """Получение лайка конкретного юзера на конкретный курс."""
    result = await session.execute(
        select(Like).where(
            Like.user_id == user_id,
            Like.course_id == course_id,
        )
    )
    return result.scalar_one_or_none()


async def count_by_course(session: AsyncSession, course_id: int) -> int:
    """Общее количество лайков на курсе."""
    result = await session.execute(select(func.count(Like.id)).where(Like.course_id == course_id))
    return result.scalar_one()


async def toggle(session: AsyncSession, user_id: int, course_id: int) -> tuple[bool, int]:
    """
    Поставить или убрать лайк.

    Возвращает кортеж: (liked: bool, total_likes: int)
    - liked=True  → лайк поставлен
    - liked=False → лайк убран
    - total_likes → актуальное количество лайков на курсе
    """
    existing = await get_by_user_and_course(session, user_id, course_id)

    if existing:
        await session.delete(existing)
        await session.commit()
        liked = False
    else:
        like = Like(user_id=user_id, course_id=course_id)
        session.add(like)
        await session.commit()
        liked = True

    total = await count_by_course(session, course_id)
    return liked, total
