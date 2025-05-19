from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_active_auth_user, get_user_cart, get_user_or_none
from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema
from app.schemas.carts import ReadFullCartSchema
from app.schemas.orders import CreateOrderSchema, ReadExtendedOrderSchema, ReadOrderBaseSchema, UpdateOrderSchema
from app.schemas.users import ReadUserSchema
from app.use_cases.orders.active import AbstractFetchActiveOrdersUseCase
from app.use_cases.orders.create import AbstractCreateOrderUseCase
from app.use_cases.orders.fetch_all import AbstractFetchOrdersUseCase
from app.use_cases.orders.history import AbstractFetchOrdersHistoryUseCase
from app.use_cases.orders.update import AbstractUpdateOrderUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=ApiResponseSchema[list[ReadExtendedOrderSchema]])
async def get_orders_list(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchOrdersUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchOrdersUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(uow=uow),
    )


@router.get("/history", response_model=ApiResponseSchema[list[ReadExtendedOrderSchema]])
async def get_orders_history(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
    use_case: Annotated[
        AbstractFetchOrdersHistoryUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchOrdersHistoryUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(user_id=user.id, uow=uow),
    )


@router.get("/active", response_model=ApiResponseSchema[list[ReadExtendedOrderSchema]])
async def get_active_orders(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
    use_case: Annotated[
        AbstractFetchActiveOrdersUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchActiveOrdersUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(user_id=user.id, uow=uow),
    )


@router.patch("/{order_id}", response_model=ApiResponseSchema[ReadOrderBaseSchema])
async def update_order_info(
    order_id: int,
    order_in: UpdateOrderSchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractUpdateOrderUseCase,
        Depends(lambda: get_container().resolve(AbstractUpdateOrderUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            order_id=order_id,
            order_in=order_in,
            uow=uow,
        ),
    )


@router.post("", response_model=ApiResponseSchema[ReadOrderBaseSchema])
async def create_order(
    order_in: CreateOrderSchema,
    cart: Annotated[ReadFullCartSchema, Depends(get_user_cart)],
    user_id: Annotated[ReadUserSchema, Depends(get_user_or_none)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateOrderUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateOrderUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            order_in=order_in,
            cart=cart,
            user_id=user_id,
            uow=uow,
        ),
    )
