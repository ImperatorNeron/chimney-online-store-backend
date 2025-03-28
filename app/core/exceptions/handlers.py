from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import UniqueConstraintViolationsException
from app.schemas.api_response import ApiResponseSchema, ErrorDetail


async def base_exception_handler(request: Request, exc: BaseAppException):
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
