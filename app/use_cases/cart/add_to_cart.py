from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.cart_items import CreateCartItemSchema, ReadCartItemSchema
from app.services.cart_items import AbstractCartItemService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractAddToCartUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        pass


@dataclass
class AddToCartUseCase(AbstractAddToCartUseCase):

    cart_item_service: AbstractCartItemService

    async def execute(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        async with uow:
            return await self.cart_item_service.create_cart_item(
                uow=uow,
                cart_item_in=cart_item_in,
            )
