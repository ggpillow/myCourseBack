from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def create(session: AsyncSession, name: str) -> Category:
    category = Category(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_by_id(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def get_by_name(session: AsyncSession, name: str) -> Category | None:
    result = await session.execute(select(Category).where(Category.name == name))
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession) -> list[Category]:
    result = await session.execute(select(Category).order_by(Category.id))
    return list(result.scalars().all())


async def update(session: AsyncSession, category: Category, name: str) -> Category:
    category.name = name
    await session.commit()
    await session.refresh(category)
    return category


async def delete(session: AsyncSession, category: Category) -> None:
    await session.delete(category)
    await session.commit()
