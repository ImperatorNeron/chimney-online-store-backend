from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.cart_items import AbstractCartItemService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteFromCartUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteFromCartUseCase(AbstractDeleteFromCartUseCase):

    cart_item_service: AbstractCartItemService

    async def execute(
        self,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            return await self.cart_item_service.delete(
                id=cart_item_id,
                cart_id=cart_id,
                uow=uow,
            )
