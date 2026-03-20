import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from slowapi.errors import RateLimitExceeded

from app.api.routers import router as api_router
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import UniqueConstraintViolationsException
from app.core.exceptions.handlers import base_exception_handler, rate_limit_handler, unique_constraint_handler
from app.core.logging_config import setup_logging
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
    application = FastAPI(
        title="Chimney online shop API",
        docs_url="/api/docs",
        default_response_class=ORJSONResponse,
        debug=settings.environment != "prod",
        lifespan=lifespan,
    )

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
            from fastapi.staticfiles import StaticFiles
            from pathlib import Path
            
            upload_dir = Path("uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            application.mount(
                "/media", 
                StaticFiles(directory=upload_dir),
                name="media",
            )
            logger.info(f"Development mode: Static files mounted from 'uploads/' → /media")
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
