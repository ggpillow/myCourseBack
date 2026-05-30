from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate


async def get_by_id(db: AsyncSession, topic_id: int) -> Topic | None:
    stmt = select(Topic).where(Topic.id == topic_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_course(db: AsyncSession, course_id: int) -> list[Topic]:
    stmt = (
        select(Topic)
        .where(Topic.course_id == course_id)
        .order_by(Topic.order_index.asc(), Topic.id.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, course_id: int, data: TopicCreate) -> Topic:
    topic = Topic(course_id=course_id, **data.model_dump())
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


async def update(db: AsyncSession, topic: Topic, data: TopicUpdate) -> Topic:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(topic, field, value)
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete(db: AsyncSession, topic: Topic) -> None:
    await db.delete(topic)
    await db.commit()
