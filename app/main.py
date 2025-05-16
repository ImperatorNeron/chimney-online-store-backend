import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import router as api_router
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import UniqueConstraintViolationsException
from app.core.exceptions.handlers import base_exception_handler, unique_constraint_handler
from app.core.settings import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title="JunToSin API",
        docs_url="/api/docs",
        description="Starnavi test project for junior position.",
        default_response_class=ORJSONResponse,
        debug=True,
    )

    os.makedirs(settings.images.upload_dir, exist_ok=True)
    application.mount(
        "/uploads",
        StaticFiles(directory=settings.images.upload_dir),
        name="uploads",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(BaseAppException, base_exception_handler)
    application.add_exception_handler(
        UniqueConstraintViolationsException,
        unique_constraint_handler,
    )
    application.include_router(router=api_router)
    return application
