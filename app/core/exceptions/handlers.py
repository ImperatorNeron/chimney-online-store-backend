import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import UniqueConstraintViolationsException
from app.schemas.api_response import ApiResponseSchema, ErrorDetail


logger = logging.getLogger(__name__)


async def base_exception_handler(request: Request, exc: BaseAppException):
    logger.error(
        f"Status code: {exc.status_code} | BaseAppException: {exc.error_code} | "
        f"{exc.detail} | URL: {request.url} | Meta: {exc.meta}",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponseSchema(
            data=None,
            errors=[
                ErrorDetail(
                    code=exc.error_code,
                    message=exc.detail,
                    meta=exc.meta,
                ),
            ],
        ).model_dump(),
    )


async def unique_constraint_handler(
    request: Request,
    exc: UniqueConstraintViolationsException,
):
    logger.error(
        f"UniqueConstraintViolationsException: {exc.error_code} | {exc.detail} | "
        f"URL: {request.url} | Violations: {exc.meta.get('violations')}",
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponseSchema(
            data=None,
            errors=[
                ErrorDetail(code=exc.error_code, message=exc.detail, meta={key: value})
                for key, value in exc.meta["violations"].items()
            ],
        ).model_dump(),
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ApiResponseSchema(
            data=None,
            errors=[
                ErrorDetail(
                    code="too_many_requests",
                    message="Ви перевищили ліміт запитів. Спробуйте пізніше.",
                    meta={},
                ),
            ],
        ).model_dump(),
    )
