import pytest

API = "/api/v1"


# ---------- helpers ----------

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


# ---------- tests ----------

@pytest.mark.asyncio
async def test_like_course_success(client, admin_headers):
    """Первый toggle → is_liked=True, likes_count=1."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C1", category_id=cat_id)
    user_headers = await _register_and_login(client, "liker1@example.com")

    r = await client.post(
        f"{API}/likes/courses/{course['id']}/toggle", headers=user_headers
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["course_id"] == course["id"]
    assert data["is_liked"] is True
    assert data["likes_count"] == 1


@pytest.mark.asyncio
async def test_like_requires_auth(client, admin_headers):
    """Без токена → 401."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C2", category_id=cat_id)

    r = await client.post(f"{API}/likes/courses/{course['id']}/toggle")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_like_nonexistent_course(client):
    """Лайк несуществующего курса → 404."""
    user_headers = await _register_and_login(client, "liker404@example.com")

    r = await client.post(
        f"{API}/likes/courses/99999/toggle", headers=user_headers
    )
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


@pytest.mark.asyncio
async def test_unlike_on_second_toggle(client, admin_headers):
    """🔥 Toggle: второй вызов снимает лайк (is_liked=False, count=0)."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C3", category_id=cat_id)
    user_headers = await _register_and_login(client, "toggler@example.com")

    # лайк
    r1 = await client.post(
        f"{API}/likes/courses/{course['id']}/toggle", headers=user_headers
    )
    assert r1.json()["is_liked"] is True
    assert r1.json()["likes_count"] == 1

    # анлайк
    r2 = await client.post(
        f"{API}/likes/courses/{course['id']}/toggle", headers=user_headers
    )
    assert r2.status_code == 200
    assert r2.json()["is_liked"] is False
    assert r2.json()["likes_count"] == 0


@pytest.mark.asyncio
async def test_like_toggle_back_and_forth(client, admin_headers):
    """🔥 Тройной toggle: ON → OFF → ON. Счётчик корректен на каждом шаге."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C4", category_id=cat_id)
    user_headers = await _register_and_login(client, "triple@example.com")

    url = f"{API}/likes/courses/{course['id']}/toggle"

    r1 = await client.post(url, headers=user_headers)
    assert r1.json() == {"course_id": course["id"], "is_liked": True, "likes_count": 1}

    r2 = await client.post(url, headers=user_headers)
    assert r2.json() == {"course_id": course["id"], "is_liked": False, "likes_count": 0}

    r3 = await client.post(url, headers=user_headers)
    assert r3.json() == {"course_id": course["id"], "is_liked": True, "likes_count": 1}


@pytest.mark.asyncio
async def test_two_users_like_independently(client, admin_headers):
    """🔥 Два разных юзера лайкают один курс → счётчик = 2."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C5", category_id=cat_id)

    user_a = await _register_and_login(client, "like_a@example.com")
    user_b = await _register_and_login(client, "like_b@example.com")

    url = f"{API}/likes/courses/{course['id']}/toggle"

    r1 = await client.post(url, headers=user_a)
    assert r1.json()["likes_count"] == 1
    assert r1.json()["is_liked"] is True

    r2 = await client.post(url, headers=user_b)
    assert r2.json()["likes_count"] == 2
    assert r2.json()["is_liked"] is True


@pytest.mark.asyncio
async def test_unlike_does_not_affect_other_user(client, admin_headers):
    """🔥 Один анлайкнул — у другого лайк остаётся, count=1."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C6", category_id=cat_id)

    user_a = await _register_and_login(client, "indep_a@example.com")
    user_b = await _register_and_login(client, "indep_b@example.com")

    url = f"{API}/likes/courses/{course['id']}/toggle"

    # оба лайкают
    await client.post(url, headers=user_a)
    await client.post(url, headers=user_b)

    # A анлайкает
    r = await client.post(url, headers=user_a)
    assert r.json()["is_liked"] is False
    assert r.json()["likes_count"] == 1

    # B снова жмёт — для него это unlike (он уже лайкнул)
    r = await client.post(url, headers=user_b)
    assert r.json()["is_liked"] is False
    assert r.json()["likes_count"] == 0