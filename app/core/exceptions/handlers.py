from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base import BaseAppException
from app.schemas.api_response import ApiResponseSchema


async def base_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponseSchema(
            data=None,
            errors=[exc.detail],
        ).model_dump(),
    )
