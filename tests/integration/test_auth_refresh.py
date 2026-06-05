import pytest
from httpx import AsyncClient

API = "/api"


async def _register_and_login(client: AsyncClient, email: str) -> dict:
    """Хелпер: регистрирует юзера и логинит, возвращает токены."""
    await client.post(
        f"{API}/auth/register",
        json={
            "email": email,
            "full_name": "Refresh User",
            "password": "strongpass123",
        },
    )
    r = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": "strongpass123"},
    )
    assert r.status_code == 200
    return r.json()


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    tokens = await _register_and_login(client, "refresh_ok@example.com")

    response = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"].count(".") == 2
    assert data["refresh_token"].count(".") == 2


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": "not.a.valid.jwt"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token(client: AsyncClient):
    """В refresh нельзя подсовывать access-токен."""
    tokens = await _register_and_login(client, "refresh_wrong_type@example.com")

    response = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_empty_token(client: AsyncClient):
    response = await client.post(
        f"{API}/auth/refresh",
        json={"refresh_token": ""},
    )
    assert response.status_code in (401, 422)
