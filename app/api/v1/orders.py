from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.v1.dependencies import (
    get_current_active_auth_superuser,
    get_current_active_auth_user,
    get_user_cart,
    get_user_or_none,
)
from app.core.containers import get_container
from app.core.limiter import limiter
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.carts import ReadFullCartSchema
from app.schemas.filters import (
    CustomerFiltersSchema,
    CustomerSortOrderSchema,
    OrderFiltersSchema,
    OrderSortOrderSchema,
    PaginationIn,
)
from app.schemas.orders import (
    CreateOrderSchema,
    ReadCustomerSchema,
    ReadExtendedOrderSchema,
    ReadOrderBaseSchema,
    UpdateOrderSchema,
)
from app.schemas.users import ReadUserSchema
from app.use_cases.orders.active import AbstractFetchActiveOrdersUseCase
from app.use_cases.orders.create import AbstractCreateOrderUseCase
from app.use_cases.orders.fetch_all import AbstractFetchOrdersUseCase
from app.use_cases.orders.fetch_customers import AbstractFetchCustomersUseCase
from app.use_cases.orders.history import AbstractFetchOrdersHistoryUseCase
from app.use_cases.orders.update import AbstractUpdateOrderUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get(
    "",
    response_model=ApiResponseSchema[ListPaginatedResponse[ReadExtendedOrderSchema]],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def get_orders_list(
    filters: Annotated[OrderFiltersSchema, Depends()],
    sort_params: Annotated[OrderSortOrderSchema, Depends()],
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchOrdersUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchOrdersUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            filters=filters,
            sort_params=sort_params,
            pagination_in=pagination_in,
            uow=uow,
        ),
    )


@router.get(
    "/customers",
    response_model=ApiResponseSchema[ListPaginatedResponse[ReadCustomerSchema]],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def get_customers_list(
    filters: Annotated[CustomerFiltersSchema, Depends()],
    sort_params: Annotated[CustomerSortOrderSchema, Depends()],
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchCustomersUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchCustomersUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            filters=filters,
            sort_params=sort_params,
            pagination_in=pagination_in,
            uow=uow,
        ),
    )


@router.get("/history", response_model=ApiResponseSchema[ListPaginatedResponse[ReadExtendedOrderSchema]])
async def get_orders_history(
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
    use_case: Annotated[
        AbstractFetchOrdersHistoryUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchOrdersHistoryUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(user_id=user.id, pagination_in=pagination_in, uow=uow),
    )


@router.get("/active", response_model=ApiResponseSchema[ListPaginatedResponse[ReadExtendedOrderSchema]])
async def get_active_orders(
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
    use_case: Annotated[
        AbstractFetchActiveOrdersUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchActiveOrdersUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(user_id=user.id, pagination_in=pagination_in, uow=uow),
    )


@router.patch(
    "/{order_id}",
    response_model=ApiResponseSchema[ReadOrderBaseSchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
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


@router.post(
    "",
    response_model=ApiResponseSchema[ReadOrderBaseSchema],
    dependencies=[],
)
@limiter.limit("10/minute")
async def create_order(
    request: Request,
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
