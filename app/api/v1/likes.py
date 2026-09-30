from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.v1.dependencies import get_current_active_auth_user
from app.core.containers import get_container
from app.core.limiter import limiter
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.filters import PaginationIn
from app.schemas.likes import CreateLikeSchema, ReadLikeSchema
from app.schemas.products import ReadPreviewProductSchema
from app.schemas.users import ReadUserSchema
from app.use_cases.like.create import AbstractCreateLikeUseCase
from app.use_cases.like.delete import AbstractDeleteLikeUseCase
from app.use_cases.like.fetch_all import AbstractFetchLikesUseCase
from app.use_cases.like.fetch_liked_products import AbstractFetchLikedProductsUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/like", tags=["Like"])


@router.get(
    "/products",
    response_model=ApiResponseSchema[ListPaginatedResponse[ReadPreviewProductSchema]],
)
async def get_liked_products(
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
    use_case: Annotated[
        AbstractFetchLikedProductsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchLikedProductsUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            user_id=user.id,
            pagination_in=pagination_in,
            uow=uow,
        ),
    )


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
@limiter.limit("60/minute")
async def create_like(
    request: Request,
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
@limiter.limit("60/minute")
async def delete_like(
    request: Request,
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
