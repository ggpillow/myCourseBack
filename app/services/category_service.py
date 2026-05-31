"""
Сервис управления категориями курсов.

Содержит бизнес-логику CRUD над категориями:
- получение списка и единичной категории (с конвертацией отсутствия в 404);
- создание с проверкой уникальности имени;
- переименование с проверкой, что новое имя не занято другой категорией;
- удаление.

Сервис изолирует роутер от прямой работы с CRUD-слоем и инкапсулирует
правило уникальности имени — чтобы оно проверялось одинаково везде.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.crud import category as crud
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_or_404(db: AsyncSession, category_id: int) -> Category:
    obj = await crud.get_by_id(db, category_id)
    if obj is None:
        raise NotFoundError("Категория не найдена")
    return obj


async def get_category(db: AsyncSession, category_id: int) -> Category:
    """Алиас для роутера."""
    return await get_or_404(db, category_id)


async def list_categories(db: AsyncSession) -> list[Category]:
    return await crud.get_all(db)


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    if await crud.get_by_name(db, data.name) is not None:
        raise AlreadyExistsError("Категория с таким названием уже существует")
    return await crud.create(db, data.name)  # ← .name


async def update_category(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category:
    category = await get_or_404(db, category_id)
    new_name = data.name
    if new_name and new_name != category.name:
        existing = await crud.get_by_name(db, new_name)
        if existing is not None and existing.id != category.id:
            raise AlreadyExistsError("Категория с таким названием уже существует")
        return await crud.update(db, category, new_name)  # ← .name
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    category = await get_or_404(db, category_id)
    await crud.delete(db, category)
