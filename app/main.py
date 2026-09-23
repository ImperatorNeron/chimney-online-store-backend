import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routers import router as api_router
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import UniqueConstraintViolationsException
from app.core.exceptions.handlers import base_exception_handler, rate_limit_handler, unique_constraint_handler
from app.core.limiter import limiter
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.settings import settings


setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend())
    logger.info("Cache initialized.")
    yield


def create_app() -> FastAPI:
    logger.info("Starting application setup...")
    is_prod = settings.environment == "prod"
    application = FastAPI(
        title="Chimney online shop API",
        # Docs/OpenAPI disabled in prod so admin API surface is not public.
        docs_url=None if is_prod else "/api/docs",
        redoc_url=None if is_prod else "/api/redoc",
        openapi_url=None if is_prod else "/api/openapi.json",
        default_response_class=ORJSONResponse,
        debug=not is_prod,
        lifespan=lifespan,
    )
    application.state.limiter = limiter
    application.add_middleware(SlowAPIMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS middleware added.")

    if settings.environment != "prod":
        try:
            from pathlib import Path

            from fastapi.staticfiles import StaticFiles

            upload_dir = Path("uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            application.mount(
                "/media",
                StaticFiles(directory=upload_dir),
                name="media",
            )
            logger.info("Development mode: Static files mounted from 'uploads/' → /media")
        except Exception as e:
            logger.error(f"Failed to mount static files in development mode: {e}")
    else:
        logger.info("Production mode: Static files disabled, using Supabase storage")

    application.add_exception_handler(BaseAppException, base_exception_handler)
    application.add_exception_handler(
        UniqueConstraintViolationsException,
        unique_constraint_handler,
    )
    application.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    application.include_router(router=api_router)
    logger.info("API routers included.")
    logger.info("Application setup complete.")
    return application
