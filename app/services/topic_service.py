"""
Сервис управления темами (уроками) и контролем доступа к ним.

Покрывает:
- CRUD над темами в рамках конкретного курса;
- получение списка тем курса;
- get_topic_for_user — ключевая функция контроля доступа: возвращает
  тему, если она бесплатная, пользователь — админ, или у него есть
  покупка курса; в остальных случаях кидает 403.

Логика "кто что видит" единая со сборкой страницы курса в
course_service.build_course_detail.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.crud import purchase as purchase_crud
from app.crud import topic as crud
from app.models.topic import Topic
from app.models.user import User, UserRole
from app.schemas.topic import TopicCreate, TopicUpdate
from app.services import course_service


async def get_or_404(db: AsyncSession, topic_id: int) -> Topic:
    topic = await crud.get_by_id(db, topic_id)
    if topic is None:
        raise NotFoundError("Тема не найдена")
    return topic


async def list_for_course(db: AsyncSession, course_id: int) -> list[Topic]:
    await course_service.get_or_404(db, course_id)
    return await crud.list_by_course(db, course_id)


async def get_topic_for_user(db: AsyncSession, topic_id: int, user: User | None) -> Topic:
    topic = await get_or_404(db, topic_id)

    is_admin = user is not None and user.role == UserRole.ADMIN
    if topic.is_free or is_admin:
        return topic

    if user is None:
        raise PermissionDeniedError("Требуется авторизация и покупка курса")

    if not await purchase_crud.exists(db, user.id, topic.course_id):
        raise PermissionDeniedError("Курс не куплен")

    return topic


async def create_topic(db: AsyncSession, course_id: int, data: TopicCreate) -> Topic:
    await course_service.get_or_404(db, course_id)
    return await crud.create(db, course_id, data)


async def update_topic(db: AsyncSession, topic_id: int, data: TopicUpdate) -> Topic:
    topic = await get_or_404(db, topic_id)
    return await crud.update(db, topic, data)


async def delete_topic(db: AsyncSession, topic_id: int) -> None:
    topic = await get_or_404(db, topic_id)
    await crud.delete(db, topic)
