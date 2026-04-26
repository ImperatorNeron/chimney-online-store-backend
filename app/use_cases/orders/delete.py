from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteOrderUseCase(ABC):

    @abstractmethod
    async def execute(self, order_id: int, uow: AbstractUnitOfWork) -> None: ...


@dataclass
class DeleteOrderUseCase(AbstractDeleteOrderUseCase):

    order_service: AbstractOrderService

    async def execute(self, order_id: int, uow: AbstractUnitOfWork) -> None:
        async with uow:
            await self.order_service.delete(uow=uow, id=order_id)
