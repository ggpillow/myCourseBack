import pytest
from httpx import AsyncClient

API = "/api/v1"


async def _register_and_login(client: AsyncClient, email: str) -> dict:
    await client.post(
        f"{API}/auth/register",
        json={
            "email": email,
            "full_name": "User Name",
            "password": "strongpass123",
        },
    )
    r = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": "strongpass123"},
    )
    return r.json()


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    email = "me_ok@example.com"
    tokens = await _register_and_login(client, email)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.get(f"{API}/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "User Name"
    assert "id" in data
    assert "role" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get(f"{API}/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_me_full_name(client: AsyncClient):
    tokens = await _register_and_login(client, "me_patch@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.patch(
        f"{API}/users/me",
        headers=headers,
        json={"full_name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name"


@pytest.mark.asyncio
async def test_patch_me_email(client: AsyncClient):
    tokens = await _register_and_login(client, "me_email_old@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.patch(
        f"{API}/users/me",
        headers=headers,
        json={"email": "me_email_new@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me_email_new@example.com"


@pytest.mark.asyncio
async def test_patch_me_unauthorized(client: AsyncClient):
    response = await client.patch(
        f"{API}/users/me",
        json={"full_name": "Hacker"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    tokens = await _register_and_login(client, "user_by_id@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    me = await client.get(f"{API}/users/me", headers=headers)
    user_id = me.json()["id"]

    response = await client.get(f"{API}/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client: AsyncClient):
    tokens = await _register_and_login(client, "user_404@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.get(f"{API}/users/999999", headers=headers)
    assert response.status_code == 404