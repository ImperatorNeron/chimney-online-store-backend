from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_user_cart
from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema
from app.schemas.cart_items import CreateCartItemSchema, CreateCartItemWithoutCartIdSchema, ReadCartItemSchema
from app.schemas.carts import ReadFullCartSchema
from app.schemas.users import ReadUserSchema
from app.use_cases.cart.add_to_cart import AbstractAddToCartUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/cart", tags=["Carts"])


@router.get("", response_model=ApiResponseSchema[ReadFullCartSchema])
async def get_cart(
    cart: Annotated[ReadUserSchema, Depends(get_user_cart)],
):
    return ApiResponseSchema(
        data=cart,
    )


@router.post("", response_model=ApiResponseSchema[ReadCartItemSchema])
async def add_to_cart(
    cart_item_in: CreateCartItemWithoutCartIdSchema,
    cart: Annotated[ReadUserSchema, Depends(get_user_cart)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractAddToCartUseCase,
        Depends(lambda: get_container().resolve(AbstractAddToCartUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            cart_item_in=CreateCartItemSchema(
                **cart_item_in.model_dump(),
                cart_id=cart.id,
            ),
            uow=uow,
        ),
    )
