from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.v1.dependencies import get_user_cart
from app.core.containers import get_container
from app.core.limiter import limiter
from app.schemas.api_response import ApiResponseSchema
from app.schemas.cart_items import (
    CreateCartItemSchema,
    CreateCartItemWithoutCartIdSchema,
    ReadCartItemSchema,
    UpdateCartItemQuantity,
)
from app.schemas.carts import ReadFullCartSchema
from app.use_cases.cart.change_items_quantity import AbstractChangeItemQuantityUseCase
from app.use_cases.cart.create_cart_item import AbstractAddToCartUseCase
from app.use_cases.cart.delete_item import AbstractDeleteFromCartUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/cart", tags=["Carts"])


@router.get("", response_model=ApiResponseSchema[ReadFullCartSchema])
async def get_cart(
    cart: Annotated[ReadFullCartSchema, Depends(get_user_cart)],
):
    return ApiResponseSchema(
        data=cart,
    )


@router.post("", response_model=ApiResponseSchema[ReadCartItemSchema])
@limiter.limit("60/minute")
async def add_to_cart(
    request: Request,
    cart_item_in: CreateCartItemWithoutCartIdSchema,
    cart: Annotated[ReadFullCartSchema, Depends(get_user_cart)],
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


@router.patch(
    "/change-item-quantity/{cart_item_id}",
    response_model=ApiResponseSchema[ReadCartItemSchema],
)
@limiter.limit("120/minute")
async def update_cart_item_quantity(
    request: Request,
    cart_item_id: int,
    cart_item_in: UpdateCartItemQuantity,
    cart: Annotated[ReadFullCartSchema, Depends(get_user_cart)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractChangeItemQuantityUseCase,
        Depends(lambda: get_container().resolve(AbstractChangeItemQuantityUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            cart_item_in=cart_item_in,
            cart_item_id=cart_item_id,
            cart_id=cart.id,
            uow=uow,
        ),
    )


@router.delete("/{cart_item_id}", response_model=None)
async def remove_item_from_cart(
    cart_item_id: int,
    cart: Annotated[ReadFullCartSchema, Depends(get_user_cart)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractDeleteFromCartUseCase,
        Depends(lambda: get_container().resolve(AbstractDeleteFromCartUseCase)),
    ],
):
    await use_case.execute(cart_item_id=cart_item_id, cart_id=cart.id, uow=uow)
