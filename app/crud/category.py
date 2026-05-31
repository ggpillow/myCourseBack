from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def create(session: AsyncSession, name: str) -> Category:
    """
    Создаёт новую категорию.

    Уникальность имени гарантируется UniqueConstraint на уровне БД —
    при попытке создать дубликат будет ошибка целостности, которую
    обрабатывает сервисный слой.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        name: Имя новой категории.

    Returns:
        Созданная категория с заполненным id.
    """

    category = Category(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_by_id(session: AsyncSession, category_id: int) -> Category | None:
    """
    Получает категорию по первичному ключу.

    Использует session.get() — самый быстрый способ загрузки по PK,
    с автоматическим кэшированием в identity map в рамках сессии.

    Returns:
        Объект Category или None, если не найден.
    """

    return await session.get(Category, category_id)


async def get_by_name(session: AsyncSession, name: str) -> Category | None:
    """
    Получает категорию по имени.

    Используется для проверки дубликатов перед созданием.

    Returns:
        Объект Category или None, если не найден.
    """

    result = await session.execute(select(Category).where(Category.name == name))
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession) -> list[Category]:
    """
    Возвращает все категории, отсортированные по id.

    Категорий обычно немного (десятки), поэтому пагинация не нужна —
    можно вернуть весь список одним запросом.
    """

    result = await session.execute(select(Category).order_by(Category.id))
    return list(result.scalars().all())


async def update(session: AsyncSession, category: Category, name: str) -> Category:
    """
    Переименовывает существующую категорию.

    Args:
        category: ORM-объект категории (получен заранее через get_by_id).
        name: Новое имя.

    Returns:
        Обновлённая категория.
    """

    category.name = name
    await session.commit()
    await session.refresh(category)
    return category


async def delete(session: AsyncSession, category: Category) -> None:
    """
    Удаляет категорию.

    Поведение при наличии связанных курсов определяется FK-стратегией
    в модели (RESTRICT / CASCADE / SET NULL).
    """

    await session.delete(category)
    await session.commit()
