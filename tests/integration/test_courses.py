import pytest

API = "/api"

async def _create_category(client, admin_headers, name: str) -> int:
    r = await client.post(
        f"{API}/categories",
        json={"name": name},
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _create_course(
    client,
    admin_headers,
    *,
    title: str,
    category_id: int,
    description: str = "desc",
    price: int = 100,
) -> dict:
    r = await client.post(
        f"{API}/courses",
        json={
            "title": title,
            "description": description,
            "price": price,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    return r.json()

@pytest.mark.asyncio
async def test_create_course_as_admin(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "Programming")

    r = await client.post(
        f"{API}/courses",
        json={
            "title": "Python Basics",
            "description": "Intro course",
            "price": 999,
            "category_id": cat_id,
        },
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Python Basics"
    assert data["price"] == 999
    assert data["category"]["id"] == cat_id
    assert data["likes_count"] == 0
    assert data["topics_count"] == 0


@pytest.mark.asyncio
async def test_create_course_requires_admin(client):
    r = await client.post(
        f"{API}/courses",
        json={"title": "X", "category_id": 1},
    )
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_course_as_regular_user_forbidden(client):
    await client.post(
        f"{API}/auth/register",
        json={
            "email": "user@example.com",
            "full_name": "Regular",
            "password": "pass12345",
        },
    )
    login = await client.post(
        f"{API}/auth/login",
        json={"email": "user@example.com", "password": "pass12345"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        f"{API}/courses",
        json={"title": "X", "category_id": 1},
        headers=headers,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_create_course_invalid_category(client, admin_headers):
    r = await client.post(
        f"{API}/courses",
        json={
            "title": "Ghost",
            "description": "",
            "price": 0,
            "category_id": 999999,
        },
        headers=admin_headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_list_courses(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "Music")
    await _create_course(client, admin_headers, title="Guitar 1", category_id=cat_id)
    await _create_course(client, admin_headers, title="Guitar 2", category_id=cat_id)

    r = await client.get(f"{API}/courses")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    titles = [c["title"] for c in data]
    assert "Guitar 1" in titles
    assert "Guitar 2" in titles


@pytest.mark.asyncio
async def test_list_courses_filter_by_category(client, admin_headers):
    cat_a = await _create_category(client, admin_headers, "CatA")
    cat_b = await _create_category(client, admin_headers, "CatB")

    await _create_course(client, admin_headers, title="A1", category_id=cat_a)
    await _create_course(client, admin_headers, title="A2", category_id=cat_a)
    await _create_course(client, admin_headers, title="B1", category_id=cat_b)

    r = await client.get(f"{API}/courses", params={"category_id": cat_a})
    assert r.status_code == 200
    titles = [c["title"] for c in r.json()]
    assert "A1" in titles and "A2" in titles
    assert "B1" not in titles


@pytest.mark.asyncio
async def test_list_courses_pagination(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "Paginated")
    for i in range(5):
        await _create_course(
            client, admin_headers, title=f"Course {i}", category_id=cat_id
        )

    r = await client.get(f"{API}/courses", params={"limit": 2, "skip": 0})
    assert r.status_code == 200
    assert len(r.json()) == 2


@pytest.mark.asyncio
async def test_get_course_detail(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "Detail")
    created = await _create_course(
        client, admin_headers, title="Deep Course", category_id=cat_id
    )

    r = await client.get(f"{API}/courses/{created['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == created["id"]
    assert data["title"] == "Deep Course"
    assert data["is_purchased"] is False
    assert data["is_liked"] is False
    assert isinstance(data["topics"], list)


@pytest.mark.asyncio
async def test_get_course_not_found(client):
    r = await client.get(f"{API}/courses/999999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_course(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "ForUpdate")
    created = await _create_course(
        client, admin_headers, title="Old Title", category_id=cat_id, price=100
    )

    r = await client.patch(
        f"{API}/courses/{created['id']}",
        json={"title": "New Title", "price": 500},
        headers=admin_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "New Title"
    assert data["price"] == 500


@pytest.mark.asyncio
async def test_update_course_not_found(client, admin_headers):
    r = await client.patch(
        f"{API}/courses/999999",
        json={"title": "X"},
        headers=admin_headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_course(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "ForDelete")
    created = await _create_course(
        client, admin_headers, title="Doomed", category_id=cat_id
    )

    r = await client.delete(
        f"{API}/courses/{created['id']}", headers=admin_headers
    )
    assert r.status_code == 204

    r = await client.get(f"{API}/courses/{created['id']}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_popular_courses_endpoint(client, admin_headers):
    cat_id = await _create_category(client, admin_headers, "Popular")
    await _create_course(client, admin_headers, title="P1", category_id=cat_id)
    await _create_course(client, admin_headers, title="P2", category_id=cat_id)

    r = await client.get(f"{API}/courses/popular", params={"limit": 5})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
