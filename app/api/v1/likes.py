from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_active_auth_user
from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema
from app.schemas.likes import CreateLikeSchema, ReadLikeSchema
from app.schemas.users import ReadUserSchema
from app.use_cases.like.create import AbstractCreateLikeUseCase
from app.use_cases.like.delete import AbstractDeleteLikeUseCase
from app.use_cases.like.fetch_all import AbstractFetchLikesUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/like", tags=["Like"])


@router.get("", response_model=ApiResponseSchema[list[int]])
async def get_likes_list(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchLikesUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchLikesUseCase)),
    ],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            user_id=user.id,
        ),
    )


@router.post(
    "",
    response_model=ApiResponseSchema[ReadLikeSchema],
)
async def create_like(
    product_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateLikeUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateLikeUseCase)),
    ],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            like_in=CreateLikeSchema(
                user_id=user.id,
                product_id=product_id,
            ),
        ),
    )


@router.delete("/{product_id}")
async def delete_like(
    product_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractDeleteLikeUseCase,
        Depends(lambda: get_container().resolve(AbstractDeleteLikeUseCase)),
    ],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            product_id=product_id,
            user_id=user.id,
        ),
    )
