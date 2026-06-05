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


async def _create_course(client, admin_headers, *, title: str, category_id: int) -> dict:
    r = await client.post(
        f"{API}/courses",
        json={
            "title": title,
            "description": "desc",
            "price": 100,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _register_and_login(client, email: str, password: str = "pass12345") -> dict:
    await client.post(
        f"{API}/auth/register",
        json={"email": email, "full_name": "User", "password": password},
    )
    r = await client.post(
        f"{API}/auth/login",
        json={"email": email, "password": password},
    )
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_buy_course_success(client, admin_headers):
    """Успешная покупка → 201 + корректная схема PurchaseRead."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C1", category_id=cat_id)

    user_headers = await _register_and_login(client, "buyer1@example.com")

    r = await client.post(
        f"{API}/purchases/courses/{course['id']}", headers=user_headers
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["course_id"] == course["id"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_buy_course_requires_auth(client, admin_headers):
    """Без токена покупка невозможна → 401."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C2", category_id=cat_id)

    r = await client.post(f"{API}/purchases/courses/{course['id']}")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_buy_course_not_found(client):
    """Покупка несуществующего курса → 404."""
    user_headers = await _register_and_login(client, "buyer404@example.com")

    r = await client.post(
        f"{API}/purchases/courses/99999", headers=user_headers
    )
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


@pytest.mark.asyncio
async def test_buy_course_twice_forbidden(client, admin_headers):
    """Двойная покупка одного курса → 409 already_exists. 🔥 Бизнес-критично."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C3", category_id=cat_id)

    user_headers = await _register_and_login(client, "double@example.com")

    r1 = await client.post(
        f"{API}/purchases/courses/{course['id']}", headers=user_headers
    )
    assert r1.status_code == 201

    r2 = await client.post(
        f"{API}/purchases/courses/{course['id']}", headers=user_headers
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["code"] == "already_exists"


@pytest.mark.asyncio
async def test_my_purchases_empty(client):
    """Свежий пользователь → пустой список покупок."""
    user_headers = await _register_and_login(client, "empty@example.com")

    r = await client.get(f"{API}/purchases/my", headers=user_headers)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_my_purchases_requires_auth(client):
    """GET /purchases/my без токена → 401."""
    r = await client.get(f"{API}/purchases/my")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_my_purchases_after_buying(client, admin_headers):
    """После покупки курс появляется в /my, поля корректны."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C4", category_id=cat_id)

    user_headers = await _register_and_login(client, "afterbuy@example.com")

    await client.post(
        f"{API}/purchases/courses/{course['id']}", headers=user_headers
    )

    r = await client.get(f"{API}/purchases/my", headers=user_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["course_id"] == course["id"]
    assert "id" in data[0]
    assert "created_at" in data[0]


@pytest.mark.asyncio
async def test_my_purchases_returns_only_own(client, admin_headers):
    """🔥 Безопасность: юзер A не видит покупки юзера B."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C5", category_id=cat_id)

    user_a = await _register_and_login(client, "user_a@example.com")
    user_b = await _register_and_login(client, "user_b@example.com")

    r = await client.post(
        f"{API}/purchases/courses/{course['id']}", headers=user_a
    )
    assert r.status_code == 201

    r = await client.get(f"{API}/purchases/my", headers=user_b)
    assert r.status_code == 200
    assert r.json() == []

    r = await client.get(f"{API}/purchases/my", headers=user_a)
    assert r.status_code == 200
    assert len(r.json()) == 1
