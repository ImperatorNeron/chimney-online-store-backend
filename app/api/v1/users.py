from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.v1.dependencies import get_current_active_auth_user
from app.core.containers import get_container
from app.core.limiter import limiter
from app.schemas.api_response import ApiResponseSchema
from app.schemas.users import ReadUserSchema, UserUpdateWithPasswordSchema
from app.use_cases.users.update import AbstractUpdateUserUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ReadUserSchema,
)
async def get_authenticated_user_profile(
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
):
    return user


@router.patch(
    "/me/update",
    response_model=ApiResponseSchema[ReadUserSchema],
)
@limiter.limit("20/minute")
async def update_authenticated_user_profile(
    request: Request,
    user_in: UserUpdateWithPasswordSchema,
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractUpdateUserUseCase,
        Depends(lambda: get_container().resolve(AbstractUpdateUserUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            user_in=user_in,
            user_id=user.id,
            uow=uow,
        ),
    )
