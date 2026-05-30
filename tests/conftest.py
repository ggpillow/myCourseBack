from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole

from app.models import user


from app.main import limiter as _app_limiter
from app.routers.auth import limiter as _auth_limiter

_app_limiter.enabled = False
_auth_limiter.enabled = False


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        settings.test_database_url,
        poolclass=NullPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Регистрирует юзера, повышает до admin, возвращает headers."""
    email = "admin_fixture@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Admin User",
            "password": "adminpass123",
        },
    )
    await db_session.execute(
        update(User).where(User.email == email).values(role=UserRole.ADMIN)
    )
    await db_session.commit()

    r = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "adminpass123"},
    )
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}