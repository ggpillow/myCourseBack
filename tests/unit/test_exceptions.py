import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient, ASGITransport
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AppException,
    AlreadyExistsError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    register_exception_handlers,
)


# ---------- Поведение классов исключений ----------

def test_app_exception_default_message():
    exc = AppException()
    assert exc.message == "Ошибка приложения"
    assert exc.status_code == 400
    assert exc.code == "app_error"


def test_app_exception_custom_message():
    exc = NotFoundError("Курс не найден")
    assert exc.message == "Курс не найден"
    assert exc.status_code == 404
    assert exc.code == "not_found"


@pytest.mark.parametrize(
    "exc_cls, expected_status, expected_code",
    [
        (NotFoundError, 404, "not_found"),
        (AlreadyExistsError, 409, "already_exists"),
        (PermissionDeniedError, 403, "permission_denied"),
        (UnauthorizedError, 401, "unauthorized"),
        (BadRequestError, 400, "bad_request"),
    ],
)
def test_domain_exceptions_attributes(exc_cls, expected_status, expected_code):
    exc = exc_cls()
    assert exc.status_code == expected_status
    assert exc.code == expected_code


# ---------- Интеграция хендлеров с мини-приложением ----------

@pytest.fixture
def test_app() -> FastAPI:
    """Минимальное FastAPI-приложение с зарегистрированными хендлерами."""
    app = FastAPI()
    register_exception_handlers(app)

    class Body(BaseModel):
        name: str

    @app.get("/not-found")
    async def _nf():
        raise NotFoundError("Курс не найден")

    @app.get("/conflict")
    async def _conf():
        raise AlreadyExistsError()

    @app.get("/forbidden")
    async def _forb():
        raise PermissionDeniedError()

    @app.get("/unauth")
    async def _ua():
        raise UnauthorizedError()

    @app.get("/bad")
    async def _bad():
        raise BadRequestError("Плохой запрос")

    @app.get("/http-error")
    async def _he():
        raise StarletteHTTPException(status_code=418, detail="I'm a teapot")

    @app.post("/validate")
    async def _val(body: Body):
        return body

    @app.get("/integrity")
    async def _ie():
        raise IntegrityError("stmt", {}, Exception("dup key"))

    @app.get("/boom")
    async def _boom():
        raise RuntimeError("kaboom")

    return app


@pytest.fixture
async def client(test_app: FastAPI):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_handler_not_found(client: AsyncClient):
    r = await client.get("/not-found")
    assert r.status_code == 404
    assert r.json() == {"detail": "Курс не найден", "code": "not_found"}


async def test_handler_conflict(client: AsyncClient):
    r = await client.get("/conflict")
    assert r.status_code == 409
    assert r.json()["code"] == "already_exists"


async def test_handler_forbidden(client: AsyncClient):
    r = await client.get("/forbidden")
    assert r.status_code == 403
    assert r.json()["code"] == "permission_denied"


async def test_handler_unauthorized(client: AsyncClient):
    r = await client.get("/unauth")
    assert r.status_code == 401
    assert r.json()["code"] == "unauthorized"


async def test_handler_bad_request(client: AsyncClient):
    r = await client.get("/bad")
    assert r.status_code == 400
    assert r.json() == {"detail": "Плохой запрос", "code": "bad_request"}


async def test_handler_http_exception(client: AsyncClient):
    r = await client.get("/http-error")
    assert r.status_code == 418
    assert r.json() == {"detail": "I'm a teapot", "code": "http_error"}


async def test_handler_validation_error(client: AsyncClient):
    r = await client.post("/validate", json={})  # отсутствует name
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "validation_error"
    assert body["detail"] == "Ошибка валидации входных данных"
    assert any(e["field"] == "name" for e in body["errors"])


async def test_handler_integrity_error(client: AsyncClient):
    r = await client.get("/integrity")
    assert r.status_code == 409
    assert r.json()["code"] == "integrity_error"


async def test_handler_unhandled_exception(client: AsyncClient):
    transport = ASGITransport(app=client._transport.app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/boom")
    assert r.status_code == 500
    assert r.json()["code"] == "internal_error"
