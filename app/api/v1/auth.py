from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from punq import Container

from app.api.v1.dependencies import get_current_auth_user_for_refresh, refresh_check
from app.core.containers import get_container
from app.core.limiter import limiter
from app.core.settings import settings
from app.schemas.api_response import ApiResponseSchema
from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import LoginUserSchema, ReadUserSchema, RegisterUserSchema
from app.use_cases.auth.login import LoginUserUseCase
from app.use_cases.auth.refresh import RefreshTokenUseCase
from app.use_cases.auth.registration import RegisterUserUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ApiResponseSchema[ReadUserSchema],
)
@limiter.limit("10/minute")
async def register(
    request: Request,
    user_in: RegisterUserSchema,
    container: Annotated[Container, Depends(get_container)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
):
    use_case: RegisterUserUseCase = container.resolve(RegisterUserUseCase)
    return ApiResponseSchema(
        data=await use_case.execute(
            user_in=user_in,
            uow=uow,
        ),
    )


@router.post(
    "/login",
    response_model=TokenInfoSchema,
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    user_in: LoginUserSchema,
    response: Response,
    container: Annotated[Container, Depends(get_container)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
):
    use_case: LoginUserUseCase = container.resolve(LoginUserUseCase)
    return await use_case.execute(response=response, uow=uow, user_in=user_in)


@router.post(
    "/refresh",
    response_model=TokenInfoSchema,
)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    user: Annotated[ReadUserSchema, Depends(get_current_auth_user_for_refresh)],
    container: Annotated[Container, Depends(get_container)],
):
    use_case: RefreshTokenUseCase = container.resolve(RefreshTokenUseCase)
    return await use_case.execute(user=user)


@router.get("/refresh-check")
async def check_refresh_token(
    refresh_check: Annotated[bool, Depends(refresh_check)],
):
    return refresh_check


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        secure=settings.session.session_secure,
        httponly=settings.session.session_httponly,
        samesite=settings.session.same_site,
    )
