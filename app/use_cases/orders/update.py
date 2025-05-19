from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.orders import ReadOrderBaseSchema, UpdateOrderSchema
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateOrderUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        order_id: int,
        order_in: UpdateOrderSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadOrderBaseSchema: ...


@dataclass
class UpdateOrderUseCase(AbstractUpdateOrderUseCase):

    order_service: AbstractOrderService

    async def execute(
        self,
        order_id: int,
        order_in: UpdateOrderSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadOrderBaseSchema:
        async with uow:
            order_in.waybill_number = order_in.waybill_number or None

            return await self.order_service.update_info(
                order_id=order_id,
                order_in=order_in,
                uow=uow,
            )
