from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
)

from punq import Container

from app.api.v1.dependencies import get_current_auth_user_for_refresh
from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema
from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import (
    LoginUserSchema,
    ReadUserSchema,
    RegisterUserSchema,
)
from app.use_cases.auth.login import LoginUserUseCase
from app.use_cases.auth.refresh import RefreshTokenUseCase
from app.use_cases.auth.registration import RegisterUserUseCase
from app.utils.unit_of_work import (
    AbstractUnitOfWork,
    UnitOfWork,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ApiResponseSchema[ReadUserSchema],
)
async def register(
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
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    container: Annotated[Container, Depends(get_container)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
):
    use_case: LoginUserUseCase = container.resolve(LoginUserUseCase)
    user_in = LoginUserSchema(username=username, password=password)
    return await use_case.execute(uow=uow, user_in=user_in)


@router.post(
    "/refresh",
    response_model=TokenInfoSchema,
)
async def refresh(
    user: Annotated[ReadUserSchema, Depends(get_current_auth_user_for_refresh)],
    container: Annotated[Container, Depends(get_container)],
):
    use_case: RefreshTokenUseCase = container.resolve(RefreshTokenUseCase)
    return await use_case.execute(user=user)
