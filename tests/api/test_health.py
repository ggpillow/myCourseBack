import pytest
from httpx import AsyncClient, ASGITransport

# ВАЖНО: поправь импорт под свой entry-point.
# Если app живёт в main.py → from main import app
# Если в fastAPI.py            → from fastAPI import app
from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}