"""
Роутер категорий курсов.

Эндпоинты:
- GET    /categories          — список всех категорий (публично).
- GET    /categories/{id}     — одна категория (публично).
- POST   /categories          — создание категории (только админ).
- PATCH  /categories/{id}     — переименование категории (только админ).
- DELETE /categories/{id}     — удаление категории (только админ).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_admin
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await category_service.list_categories(db)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await category_service.get_category(db, category_id)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await category_service.create_category(db, data)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_admin)],
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await category_service.update_category(db, category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    await category_service.delete_category(db, category_id)