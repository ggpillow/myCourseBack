import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.routers import auth as auth_router
from app.routers import category as category_router
from app.routers import course as course_router
from app.routers import like as like_router
from app.routers import purchase as purchase_router
from app.routers import topic as topic_router
from app.routers import user as user_router

# Глобальный лимитер
limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Courses API",
        description="Платформа микрообучения: курсы, темы, покупки, лайки.",
        version="0.1.0",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration:.1f}ms)"
        )
        return response

    register_exception_handlers(app)

    api_prefix = "/api/v1"
    app.include_router(auth_router.router, prefix=api_prefix)
    app.include_router(user_router.router, prefix=api_prefix)
    app.include_router(category_router.router, prefix=api_prefix)
    app.include_router(course_router.router, prefix=api_prefix)
    app.include_router(topic_router.router, prefix=api_prefix)
    app.include_router(purchase_router.router, prefix=api_prefix)
    app.include_router(like_router.router, prefix=api_prefix)

    @app.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
