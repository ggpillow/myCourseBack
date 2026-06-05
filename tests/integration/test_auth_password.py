import pytest
from httpx import AsyncClient

API = "/api"


async def _register_and_login(client: AsyncClient, email: str, password: str = "strongpass123") -> dict:
    await client.post(
        f"{API}/auth/register",
        json={
            "email": email,
            "full_name": "Pwd User",
            "password": password,
        },
    )
    r = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200
    return r.json()


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient):
    email = "pwd_ok@example.com"
    old_password = "strongpass123"
    new_password = "newStrongPass456"

    tokens = await _register_and_login(client, email, old_password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.post(
        f"{API}/auth/change-password",
        headers=headers,
        json={"old_password": old_password, "new_password": new_password},
    )
    assert response.status_code in (200, 204)

    r_old = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": old_password},
    )
    assert r_old.status_code == 401

    r_new = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": new_password},
    )
    assert r_new.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_old(client: AsyncClient):
    tokens = await _register_and_login(client, "pwd_wrong_old@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.post(
        f"{API}/auth/change-password",
        headers=headers,
        json={"old_password": "completely_wrong", "new_password": "newStrongPass456"},
    )
    assert response.status_code in (400, 401)


@pytest.mark.asyncio
async def test_change_password_same_as_old(client: AsyncClient):
    password = "strongpass123"
    tokens = await _register_and_login(client, "pwd_same@example.com", password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.post(
        f"{API}/auth/change-password",
        headers=headers,
        json={"old_password": password, "new_password": password},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_unauthorized(client: AsyncClient):
    response = await client.post(
        f"{API}/auth/change-password",
        json={"old_password": "whatever123", "new_password": "newStrongPass456"},
    )
    assert response.status_code == 401
