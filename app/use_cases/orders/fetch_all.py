from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import OrderFiltersSchema, OrderSortOrderSchema, PaginationIn, PaginationOut
from app.schemas.orders import ReadExtendedOrderSchema
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchOrdersUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        filters: OrderFiltersSchema,
        sort_params: OrderSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadExtendedOrderSchema]: ...


@dataclass
class FetchOrdersUseCase(AbstractFetchOrdersUseCase):
    order_service: AbstractOrderService

    async def execute(
        self,
        filters: OrderFiltersSchema,
        sort_params: OrderSortOrderSchema,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadExtendedOrderSchema]:
        async with uow:
            count = await self.order_service.count(uow=uow, filters=filters)
            orders = await self.order_service.list_all(
                uow=uow,
                pagination_in=pagination_in,
                filters=filters,
                order_by=sort_params,
            )
            return ListPaginatedResponse(
                items=[
                    ReadExtendedOrderSchema(
                        **order.model_dump(),
                        total_price=await self.order_service.get_total_price(
                            order_items=order.items,
                        ),
                        total_quantity=await self.order_service.get_total_quantity(
                            order.items,
                        ),
                    )
                    for order in orders
                ],
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
