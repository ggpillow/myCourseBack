from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.crud import category as category_crud
from app.crud import course as crud
from app.crud import like as like_crud
from app.crud import purchase as purchase_crud
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate


async def get_or_404(db: AsyncSession, course_id: int) -> Course:
    course = await crud.get_by_id(db, course_id)
    if course is None:
        raise NotFoundError("Курс не найден")
    return course


async def get_with_topics_or_404(db: AsyncSession, course_id: int) -> Course:
    course = await crud.get_by_id_with_topics(db, course_id)
    if course is None:
        raise NotFoundError("Курс не найден")
    return course


async def list_catalog(
    db: AsyncSession,
    *,
    category_id: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
) -> list[Course]:
    if category_id is not None:
        if await category_crud.get_by_id(db, category_id) is None:
            raise NotFoundError("Категория не найдена")
    return await crud.list_courses(
        db,
        category_id=category_id,
        search=search,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )


async def list_popular(db: AsyncSession, limit: int = 10) -> list[Course]:
    return await crud.list_popular(db, limit=limit)


async def create_course(db: AsyncSession, data: CourseCreate) -> Course:
    if await category_crud.get_by_id(db, data.category_id) is None:
        raise NotFoundError("Категория не найдена")
    return await crud.create(db, data)


async def update_course(db: AsyncSession, course_id: int, data: CourseUpdate) -> Course:
    course = await get_or_404(db, course_id)
    if data.category_id is not None:
        if await category_crud.get_by_id(db, data.category_id) is None:
            raise NotFoundError("Категория не найдена")
    return await crud.update(db, course, data)


async def delete_course(db: AsyncSession, course_id: int) -> None:
    course = await get_or_404(db, course_id)
    await crud.delete(db, course)


async def enrich_course(db: AsyncSession, course: Course, user: User | None) -> dict:
    """Готовит dict с полями для CourseRead (likes_count, topics_count)."""
    likes_count = await crud.count_likes(db, course.id)
    topics_count = await crud.count_topics(db, course.id)
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "price": course.price,
        "created_at": course.created_at,
        "category": course.category,
        "likes_count": likes_count,
        "topics_count": topics_count,
    }


async def build_course_detail(db: AsyncSession, course_id: int, user: User | None) -> dict:
    course = await get_with_topics_or_404(db, course_id)
    likes_count = await crud.count_likes(db, course.id)
    topics_count = await crud.count_topics(db, course.id)

    is_purchased = False
    is_liked = False
    is_admin = user is not None and user.role.value == "admin"

    if user is not None:
        is_purchased = await purchase_crud.exists(db, user.id, course.id)
        is_liked = await like_crud.get_by_user_and_course(db, user.id, course.id) is not None

    # Темы: полный контент только если is_free, куплено или админ
    topics_payload = []
    for t in sorted(course.topics, key=lambda x: (x.order_index, x.id)):
        if t.is_free or is_purchased or is_admin:
            topics_payload.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "content": t.content,
                    "order_index": t.order_index,
                    "is_free": t.is_free,
                    "course_id": t.course_id,
                }
            )
        else:
            topics_payload.append(
                {
                    "id": t.id,
                    "title": t.title,
                    "order_index": t.order_index,
                    "is_free": t.is_free,
                }
            )

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "price": course.price,
        "created_at": course.created_at,
        "category": course.category,
        "likes_count": likes_count,
        "topics_count": topics_count,
        "topics": topics_payload,
        "is_purchased": is_purchased,
        "is_liked": is_liked,
    }
