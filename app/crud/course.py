from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.like import Like
from app.models.topic import Topic
from app.schemas.course import CourseCreate, CourseUpdate


async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
    stmt = select(Course).where(Course.id == course_id).options(selectinload(Course.category))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id_with_topics(db: AsyncSession, course_id: int) -> Course | None:
    stmt = (
        select(Course)
        .where(Course.id == course_id)
        .options(
            selectinload(Course.category),
            selectinload(Course.topics),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_courses(
    db: AsyncSession,
    *,
    category_id: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
) -> list[Course]:
    stmt = select(Course).options(selectinload(Course.category))

    if category_id is not None:
        stmt = stmt.where(Course.category_id == category_id)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where((Course.title.ilike(pattern)) | (Course.description.ilike(pattern)))

    # Сортировка
    sort_columns = {
        "created_at": Course.created_at,
        "price": Course.price,
        "title": Course.title,
    }
    sort_col = sort_columns.get(sort_by, Course.created_at)
    stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_popular(db: AsyncSession, limit: int = 10) -> list[Course]:
    """Топ курсов по количеству лайков."""
    likes_count = func.count(Like.id).label("likes_count")
    stmt = (
        select(Course)
        .outerjoin(Like, Like.course_id == Course.id)
        .group_by(Course.id)
        .order_by(likes_count.desc(), Course.created_at.desc())
        .options(selectinload(Course.category))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def count_likes(db: AsyncSession, course_id: int) -> int:
    stmt = select(func.count(Like.id)).where(Like.course_id == course_id)
    result = await db.execute(stmt)
    return result.scalar_one() or 0


async def count_topics(db: AsyncSession, course_id: int) -> int:
    stmt = select(func.count(Topic.id)).where(Topic.course_id == course_id)
    result = await db.execute(stmt)
    return result.scalar_one() or 0


async def create(db: AsyncSession, data: CourseCreate) -> Course:
    course = Course(**data.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return await get_by_id(db, course.id)


async def update(db: AsyncSession, course: Course, data: CourseUpdate) -> Course:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    await db.commit()
    await db.refresh(course)
    return await get_by_id(db, course.id)


async def delete(db: AsyncSession, course: Course) -> None:
    await db.delete(course)
    await db.commit()
