"""
Кастомные доменные исключения и глобальные обработчики FastAPI.

Идея:
- В сервисах/CRUD кидаем семантические исключения (NotFound, AlreadyExists, ...).
- Глобальные хендлеры конвертируют их в красивые JSON-ответы.
- Все ошибки имеют единый формат: {"detail": "...", "code": "..."}.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


# ---------- Базовый класс ----------
class AppException(Exception):
    """Базовое доменное исключение приложения."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "app_error"
    message: str = "Ошибка приложения"

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


# ---------- Конкретные доменные ошибки ----------
class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "Объект не найден"


class AlreadyExistsError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "already_exists"
    message = "Объект уже существует"


class PermissionDeniedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "permission_denied"
    message = "Недостаточно прав"


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    message = "Требуется авторизация"


class BadRequestError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"
    message = "Некорректный запрос"


# ---------- Утилита для единого формата ответа ----------
def _error_response(status_code: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "code": code},
    )


# ---------- Хендлеры ----------
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return _error_response(exc.status_code, exc.message, exc.code)


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Ошибка"
    return _error_response(exc.status_code, detail, "http_error")


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(p) for p in err["loc"] if p != "body"),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации входных данных",
            "code": "validation_error",
            "errors": errors,
        },
    )


async def integrity_error_handler(_: Request, exc: IntegrityError) -> JSONResponse:
    return _error_response(
        status.HTTP_409_CONFLICT,
        "Конфликт данных в базе (нарушено ограничение целостности)",
        "integrity_error",
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Внутренняя ошибка сервера",
        "internal_error",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все хендлеры на инстансе FastAPI."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
