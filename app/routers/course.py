from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_optional, require_admin
from app.models.user import User
from app.schemas.course import CourseCreate, CourseDetail, CourseRead, CourseUpdate
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
async def list_courses(
    category_id: int | None = Query(None, description="Фильтр по категории"),
    search: str | None = Query(None, description="Поиск по названию и описанию"),
    sort_by: str = Query(
        "created_at",
        regex="^(created_at|price|title)$",
        description="Сортировка: created_at | price | title",
    ),
    order: str = Query("desc", regex="^(asc|desc)$", description="Порядок: asc | desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    courses = await course_service.list_catalog(
        db,
        category_id=category_id,
        search=search,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )
    return [await course_service.enrich_course(db, c, user) for c in courses]


@router.get("/popular", response_model=list[CourseRead])
async def list_popular(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    courses = await course_service.list_popular(db, limit=limit)
    return [await course_service.enrich_course(db, c, user) for c in courses]


@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    return await course_service.build_course_detail(db, course_id, user)


@router.post(
    "",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
):
    course = await course_service.create_course(db, payload)
    return await course_service.enrich_course(db, course, None)


@router.patch(
    "/{course_id}",
    response_model=CourseRead,
    dependencies=[Depends(require_admin)],
)
async def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: AsyncSession = Depends(get_db),
):
    course = await course_service.update_course(db, course_id, payload)
    return await course_service.enrich_course(db, course, None)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
):
    await course_service.delete_course(db, course_id)
    return None
