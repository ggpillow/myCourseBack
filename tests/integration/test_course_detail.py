import pytest
from sqlalchemy import update

from app.models.user import User, UserRole

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


async def _create_topic(
    client,
    admin_headers,
    *,
    course_id: int,
    title: str,
    content: str,
    order_index: int,
    is_free: bool,
) -> dict:
    r = await client.post(
        f"{API}/courses/{course_id}/topics",
        json={
            "title": title,
            "content": content,
            "order_index": order_index,
            "is_free": is_free,
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


async def _promote_to_admin(db_session, email: str) -> None:
    await db_session.execute(
        update(User).where(User.email == email).values(role=UserRole.ADMIN)
    )
    await db_session.commit()

@pytest.mark.asyncio
async def test_course_detail_anon_hides_paid_content(client, admin_headers):
    """Аноним: контент платных тем скрыт (пустая строка)."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)
    await _create_topic(
        client, admin_headers,
        course_id=course["id"], title="Paid", content="SECRET",
        order_index=1, is_free=False,
    )

    r = await client.get(f"{API}/courses/{course['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["is_purchased"] is False
    assert data["is_liked"] is False
    assert len(data["topics"]) == 1
    topic = data["topics"][0]
    assert topic["title"] == "Paid"
    assert topic["is_free"] is False
    assert "SECRET" not in topic.get("content", "")


@pytest.mark.asyncio
async def test_course_detail_anon_sees_free_content(client, admin_headers):
    """Аноним: контент бесплатных тем виден."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)
    await _create_topic(
        client, admin_headers,
        course_id=course["id"], title="Free", content="OPEN-CONTENT",
        order_index=1, is_free=True,
    )

    r = await client.get(f"{API}/courses/{course['id']}")
    assert r.status_code == 200
    topic = r.json()["topics"][0]
    assert topic["is_free"] is True
    assert topic["content"] == "OPEN-CONTENT"


@pytest.mark.asyncio
async def test_course_detail_user_without_purchase_hides_paid(client, admin_headers):
    """Залогинен, но не купил — платный контент скрыт."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)
    await _create_topic(
        client, admin_headers,
        course_id=course["id"], title="Paid", content="SECRET",
        order_index=1, is_free=False,
    )

    user_headers = await _register_and_login(client, "buyer_no@example.com")

    r = await client.get(f"{API}/courses/{course['id']}", headers=user_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["is_purchased"] is False
    assert "SECRET" not in data["topics"][0].get("content", "")


@pytest.mark.asyncio
async def test_course_detail_user_after_purchase_sees_paid(client, admin_headers):
    """После покупки — платный контент открыт, is_purchased=True."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)
    await _create_topic(
        client, admin_headers,
        course_id=course["id"], title="Paid", content="GOLD",
        order_index=1, is_free=False,
    )

    user_headers = await _register_and_login(client, "buyer_yes@example.com")
    r = await client.post(
        f"{API}/purchases/courses/{course['id']}", headers=user_headers
    )
    assert r.status_code == 201, r.text

    r = await client.get(f"{API}/courses/{course['id']}", headers=user_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["is_purchased"] is True
    assert data["topics"][0]["content"] == "GOLD"


@pytest.mark.asyncio
async def test_course_detail_admin_sees_all_content(client, admin_headers, db_session):
    """Админ видит контент всех тем без покупки."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)
    await _create_topic(
        client, admin_headers,
        course_id=course["id"], title="Paid", content="ADMIN-CAN-SEE",
        order_index=1, is_free=False,
    )

    email = "second_admin@example.com"
    second_admin_headers = await _register_and_login(client, email)
    await _promote_to_admin(db_session, email)

    r = await client.get(f"{API}/courses/{course['id']}", headers=second_admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["is_purchased"] is False
    assert data["topics"][0]["content"] == "ADMIN-CAN-SEE"


@pytest.mark.asyncio
async def test_course_detail_is_liked_flag(client, admin_headers):
    """После toggle_like — is_liked=True."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)

    user_headers = await _register_and_login(client, "liker@example.com")

    r = await client.get(f"{API}/courses/{course['id']}", headers=user_headers)
    assert r.json()["is_liked"] is False

    r = await client.post(
        f"{API}/likes/courses/{course['id']}/toggle", headers=user_headers
    )
    assert r.status_code == 200, r.text

    r = await client.get(f"{API}/courses/{course['id']}", headers=user_headers)
    assert r.json()["is_liked"] is True


@pytest.mark.asyncio
async def test_course_detail_topics_ordered_by_order_index(client, admin_headers):
    """Темы возвращаются по возрастанию order_index."""
    cat_id = await _create_category(client, admin_headers, "C")
    course = await _create_course(client, admin_headers, title="Crs", category_id=cat_id)

    await _create_topic(
        client, admin_headers, course_id=course["id"],
        title="Third", content="", order_index=3, is_free=True,
    )
    await _create_topic(
        client, admin_headers, course_id=course["id"],
        title="First", content="", order_index=1, is_free=True,
    )
    await _create_topic(
        client, admin_headers, course_id=course["id"],
        title="Second", content="", order_index=2, is_free=True,
    )

    r = await client.get(f"{API}/courses/{course['id']}")
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()["topics"]]
    assert titles == ["First", "Second", "Third"]
