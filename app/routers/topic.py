"""
Роутер тем (уроков).

Эндпоинты:
- GET    /courses/{course_id}/topics — список тем курса (превью без контента).
- GET    /topics/{topic_id}          — одна тема с проверкой доступа.
- POST   /courses/{course_id}/topics — создание темы в курсе (только админ).
- PATCH  /topics/{topic_id}          — обновление темы (только админ).
- DELETE /topics/{topic_id}          — удаление темы (только админ).

Чтение конкретной темы пропущено через get_current_user_optional —
сервис сам решает, отдавать контент или 403, в зависимости от
is_free, факта покупки и роли пользователя.

Префикса у роутера нет, так как пути строятся по двум разным базам
(/courses/.../topics и /topics/...) в соответствии с REST-семантикой.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_optional, require_admin
from app.models.user import User
from app.schemas.topic import TopicCreate, TopicPreview, TopicRead, TopicUpdate
from app.services import topic_service

router = APIRouter(tags=["topics"])


@router.get("/courses/{course_id}/topics", response_model=list[TopicPreview])
async def list_course_topics(
    course_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await topic_service.list_for_course(db, course_id)


@router.get("/topics/{topic_id}", response_model=TopicRead)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    return await topic_service.get_topic_for_user(db, topic_id, user)


@router.post(
    "/courses/{course_id}/topics",
    response_model=TopicRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_topic(
    course_id: int,
    payload: TopicCreate,
    db: AsyncSession = Depends(get_db),
):
    return await topic_service.create_topic(db, course_id, payload)


@router.patch(
    "/topics/{topic_id}",
    response_model=TopicRead,
    dependencies=[Depends(require_admin)],
)
async def update_topic(
    topic_id: int,
    payload: TopicUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await topic_service.update_topic(db, topic_id, payload)


@router.delete(
    "/topics/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
):
    await topic_service.delete_topic(db, topic_id)
    return None