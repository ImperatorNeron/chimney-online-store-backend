from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import router as api_router
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.handlers import base_exception_handler


def create_app() -> FastAPI:
    application = FastAPI(
        title="JunToSin API",
        docs_url="/api/docs",
        description="Starnavi test project for junior position.",
        default_response_class=ORJSONResponse,
        debug=True,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(BaseAppException, base_exception_handler)
    application.include_router(router=api_router)
    return application
