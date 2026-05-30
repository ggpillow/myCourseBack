import pytest

API = "/api/v1"


# ---------- helpers ----------

async def _create_category(client, admin_headers, name: str) -> int:
    r = await client.post(
        f"{API}/categories", json={"name": name}, headers=admin_headers
    )
    return r.json()["id"]


async def _create_course(
    client, admin_headers, *, title: str, category_id: int, price: int = 100
) -> dict:
    r = await client.post(
        f"{API}/courses",
        json={
            "title": title,
            "description": "desc",
            "price": price,
            "category_id": category_id,
        },
        headers=admin_headers,
    )
    return r.json()


async def _register_and_login(client, email: str, password: str = "pass12345") -> dict:
    await client.post(
        f"{API}/auth/register",
        json={"email": email, "full_name": "User", "password": password},
    )
    r = await client.post(
        f"{API}/auth/login", json={"email": email, "password": password}
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _buy_course(client, user_headers, course_id: int):
    r = await client.post(
        f"{API}/purchases/courses/{course_id}", headers=user_headers
    )
    assert r.status_code in (200, 201), r.text


# ---------- CRUD & permissions ----------

@pytest.mark.asyncio
async def test_create_topic_requires_admin(client, admin_headers):
    """🔒 Обычный юзер не может создать тему."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C1", category_id=cat_id)
    user_headers = await _register_and_login(client, "topic_user@example.com")

    r = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "T1", "content": "body", "order_index": 1},
        headers=user_headers,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_create_topic_success(client, admin_headers):
    """Админ создаёт тему — успех, поля корректны."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C2", category_id=cat_id)

    r = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Intro", "content": "Hello", "order_index": 1, "is_free": True},
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Intro"
    assert data["content"] == "Hello"
    assert data["is_free"] is True
    assert data["course_id"] == course["id"]


@pytest.mark.asyncio
async def test_create_topic_in_nonexistent_course(client, admin_headers):
    """Создание темы в несуществующем курсе → 404."""
    r = await client.post(
        f"{API}/courses/99999/topics",
        json={"title": "T", "content": "x", "order_index": 1},
        headers=admin_headers,
    )
    assert r.status_code == 404


# ---------- list / preview ----------

@pytest.mark.asyncio
async def test_list_topics_returns_preview_without_content(client, admin_headers):
    """🔒 PRIVACY: список тем не содержит content (только preview)."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C3", category_id=cat_id)

    await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "T1", "content": "SECRET_CONTENT", "order_index": 1},
        headers=admin_headers,
    )

    r = await client.get(f"{API}/courses/{course['id']}/topics")
    assert r.status_code == 200
    topics = r.json()
    assert len(topics) == 1
    assert "content" not in topics[0]
    assert topics[0]["title"] == "T1"


@pytest.mark.asyncio
async def test_list_topics_ordered_by_order_index(client, admin_headers):
    """🔥 Темы возвращаются в порядке order_index, а не вставки."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C4", category_id=cat_id)

    # вставляем в обратном порядке
    for title, idx in [("Third", 3), ("First", 1), ("Second", 2)]:
        await client.post(
            f"{API}/courses/{course['id']}/topics",
            json={"title": title, "content": "x", "order_index": idx},
            headers=admin_headers,
        )

    r = await client.get(f"{API}/courses/{course['id']}/topics")
    titles = [t["title"] for t in r.json()]
    assert titles == ["First", "Second", "Third"]


# ---------- access control on GET /topics/{id} ----------

@pytest.mark.asyncio
async def test_free_topic_accessible_to_anonymous(client, admin_headers):
    """🔥 Free-тема доступна без авторизации."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C5", category_id=cat_id)

    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Free", "content": "FREE_BODY", "order_index": 1, "is_free": True},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]

    r = await client.get(f"{API}/topics/{topic_id}")
    assert r.status_code == 200
    assert r.json()["content"] == "FREE_BODY"


@pytest.mark.asyncio
async def test_paid_topic_forbidden_for_anonymous(client, admin_headers):
    """🔒 Платная тема скрыта от анонимов → 403."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C6", category_id=cat_id)

    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Paid", "content": "SECRET", "order_index": 1, "is_free": False},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]

    r = await client.get(f"{API}/topics/{topic_id}")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_paid_topic_forbidden_for_non_buyer(client, admin_headers):
    """🔒 Платная тема скрыта от залогиненного, но не купившего."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C7", category_id=cat_id)

    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Paid", "content": "SECRET", "order_index": 1, "is_free": False},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]
    user_headers = await _register_and_login(client, "non_buyer@example.com")

    r = await client.get(f"{API}/topics/{topic_id}", headers=user_headers)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_paid_topic_accessible_to_buyer(client, admin_headers):
    """🔥 Купивший видит платную тему с полным content."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C8", category_id=cat_id)

    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Paid", "content": "FULL_BODY", "order_index": 1, "is_free": False},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]

    user_headers = await _register_and_login(client, "buyer_topic@example.com")
    await _buy_course(client, user_headers, course["id"])

    r = await client.get(f"{API}/topics/{topic_id}", headers=user_headers)
    assert r.status_code == 200
    assert r.json()["content"] == "FULL_BODY"


@pytest.mark.asyncio
async def test_paid_topic_accessible_to_admin(client, admin_headers):
    """🔥 Админ видит любую платную тему без покупки."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C9", category_id=cat_id)

    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Paid", "content": "ADMIN_SEES", "order_index": 1, "is_free": False},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]

    r = await client.get(f"{API}/topics/{topic_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["content"] == "ADMIN_SEES"


# ---------- update / delete ----------

@pytest.mark.asyncio
async def test_update_topic_partial(client, admin_headers):
    """PATCH меняет только переданные поля."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C10", category_id=cat_id)

    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "Old", "content": "OldBody", "order_index": 1, "is_free": False},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]

    r = await client.patch(
        f"{API}/topics/{topic_id}",
        json={"title": "New"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "New"
    assert data["content"] == "OldBody"  # не изменился
    assert data["is_free"] is False


@pytest.mark.asyncio
async def test_delete_topic_requires_admin(client, admin_headers):
    """🔒 Удаление темы — только админ."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C11", category_id=cat_id)
    create = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "T", "content": "x", "order_index": 1},
        headers=admin_headers,
    )
    topic_id = create.json()["id"]
    user_headers = await _register_and_login(client, "del_user@example.com")

    r = await client.delete(f"{API}/topics/{topic_id}", headers=user_headers)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_delete_topic_does_not_remove_course(client, admin_headers):
    """🔥 Удаление темы не ломает курс — курс остаётся, тем стало меньше."""
    cat_id = await _create_category(client, admin_headers, "Cat")
    course = await _create_course(client, admin_headers, title="C12", category_id=cat_id)

    t1 = await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "T1", "content": "x", "order_index": 1},
        headers=admin_headers,
    )
    await client.post(
        f"{API}/courses/{course['id']}/topics",
        json={"title": "T2", "content": "y", "order_index": 2},
        headers=admin_headers,
    )

    r_del = await client.delete(
        f"{API}/topics/{t1.json()['id']}", headers=admin_headers
    )
    assert r_del.status_code == 204

    # курс жив
    r_course = await client.get(f"{API}/courses/{course['id']}")
    assert r_course.status_code == 200

    # осталась 1 тема
    r_list = await client.get(f"{API}/courses/{course['id']}/topics")
    assert len(r_list.json()) == 1
    assert r_list.json()[0]["title"] == "T2"