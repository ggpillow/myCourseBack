import pytest

API = "/api"


@pytest.mark.asyncio
async def test_create_category(client, admin_headers):
    response = await client.post(
        f"{API}/categories",
        json={"name": "Programming"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Programming"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_categories(client, admin_headers):
    await client.post(f"{API}/categories", json={"name": "Design"}, headers=admin_headers)
    await client.post(f"{API}/categories", json={"name": "Marketing"}, headers=admin_headers)

    response = await client.get(f"{API}/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [c["name"] for c in data]
    assert "Design" in names
    assert "Marketing" in names


@pytest.mark.asyncio
async def test_get_category_by_id(client, admin_headers):
    created = await client.post(
        f"{API}/categories", json={"name": "Music"}, headers=admin_headers
    )
    cid = created.json()["id"]

    response = await client.get(f"{API}/categories/{cid}")
    assert response.status_code == 200
    assert response.json()["name"] == "Music"


@pytest.mark.asyncio
async def test_get_category_not_found(client):
    response = await client.get(f"{API}/categories/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_category(client, admin_headers):
    created = await client.post(
        f"{API}/categories", json={"name": "Old Name"}, headers=admin_headers
    )
    cid = created.json()["id"]

    response = await client.patch(
        f"{API}/categories/{cid}",
        json={"name": "New Name"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_category(client, admin_headers):
    created = await client.post(
        f"{API}/categories", json={"name": "ToDelete"}, headers=admin_headers
    )
    cid = created.json()["id"]

    response = await client.delete(f"{API}/categories/{cid}", headers=admin_headers)
    assert response.status_code == 204

    check = await client.get(f"{API}/categories/{cid}")
    assert check.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_not_found(client, admin_headers):
    response = await client.delete(
        f"{API}/categories/999999", headers=admin_headers
    )
    assert response.status_code == 404