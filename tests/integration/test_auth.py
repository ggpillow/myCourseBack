import pytest
from httpx import AsyncClient

API = "/api/v1"


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        f"{API}/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "strongpass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "student"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "full_name": "Dup User",
        "password": "strongpass123",
    }
    r1 = await client.post(f"{API}/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await client.post(f"{API}/auth/register", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        f"{API}/auth/register",
        json={
            "email": "login@example.com",
            "full_name": "Login User",
            "password": "strongpass123",
        },
    )

    response = await client.post(
        f"{API}/auth/login",
        json={"email": "login@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        f"{API}/auth/register",
        json={
            "email": "wrong@example.com",
            "full_name": "Wrong Pass",
            "password": "strongpass123",
        },
    )

    response = await client.post(
        f"{API}/auth/login",
        json={"email": "wrong@example.com", "password": "wrong_password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    response = await client.post(
        f"{API}/auth/login",
        json={"email": "ghost@example.com", "password": "anyPass123"},
    )
    assert response.status_code == 401