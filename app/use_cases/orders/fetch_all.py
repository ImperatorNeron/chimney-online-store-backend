from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.orders import ReadExtendedOrderSchema
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchOrdersUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadExtendedOrderSchema]: ...


@dataclass
class FetchOrdersUseCase(AbstractFetchOrdersUseCase):
    order_service: AbstractOrderService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadExtendedOrderSchema]:
        async with uow:
            orders = await self.order_service.list_all(uow=uow)
            return [
                ReadExtendedOrderSchema(
                    **order.model_dump(),
                    total_price=await self.order_service.get_total_price(
                        order_items=order.items,
                        price_discount=order.price_discount,
                    ),
                    total_quantity=await self.order_service.get_total_quantity(
                        order.items,
                    ),
                )
                for order in orders
            ]
