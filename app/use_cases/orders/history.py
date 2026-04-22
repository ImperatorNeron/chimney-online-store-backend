from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.orders import ReadExtendedOrderSchema
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchOrdersHistoryUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadExtendedOrderSchema]: ...


@dataclass
class FetchOrdersHistoryUseCase(AbstractFetchOrdersHistoryUseCase):
    order_service: AbstractOrderService

    async def execute(
        self,
        user_id: int,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadExtendedOrderSchema]:
        async with uow:
            orders = await self.order_service.get_order_history(
                user_id=user_id,
                uow=uow,
                limit=pagination_in.limit,
                offset=pagination_in.offset,
            )
            count = await self.order_service.count(
                filters={"user_id": user_id, "status__in": ["delivered", "cancelled"]},
                uow=uow,
            )
            return ListPaginatedResponse(
                items=[
                    ReadExtendedOrderSchema(
                        **order.model_dump(),
                        total_price=await self.order_service.get_total_price(order.items),
                        total_quantity=await self.order_service.get_total_quantity(order.items),
                    )
                    for order in orders
                ],
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )
