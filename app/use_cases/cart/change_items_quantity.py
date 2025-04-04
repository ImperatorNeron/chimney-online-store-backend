from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.cart_items import ReadCartItemSchema, UpdateCartItemQuantity
from app.services.cart_items import AbstractCartItemService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractChangeItemQuantityUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        cart_item_id: int,
        cart_item_in: UpdateCartItemQuantity,
        cart: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        pass


@dataclass
class ChangeItemQuantityUseCase(AbstractChangeItemQuantityUseCase):

    cart_item_service: AbstractCartItemService

    async def execute(
        self,
        cart_item_id: int,
        cart_item_in: UpdateCartItemQuantity,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        async with uow:
            if cart_item_in.action == "increment":
                return await self.cart_item_service.increase_cart_item_quantity(
                    cart_item_id=cart_item_id,
                    quantity=cart_item_in.quantity,
                    cart_id=cart_id,
                    uow=uow,
                )
            if cart_item_in.action == "decrement":
                return await self.cart_item_service.decrease_cart_item_quantity(
                    cart_item_id=cart_item_id,
                    quantity=cart_item_in.quantity,
                    cart_id=cart_id,
                    uow=uow,
                )
