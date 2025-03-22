from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.carts import ReadFullCartSchema
from app.services.cart_items import AbstractCartItemService
from app.services.carts import AbstractCartService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchCartUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        **kwargs: dict,
    ) -> ReadFullCartSchema: ...


@dataclass
class FetchCartUseCase(AbstractFetchCartUseCase):

    cart_service: AbstractCartService
    cart_item_service: AbstractCartItemService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        **kwargs: dict,
    ) -> ReadFullCartSchema:
        async with uow:
            cart = await self.cart_service.get_cart(**kwargs, uow=uow)
            total_quantity = self.cart_service.get_total_quantity(cart.items)
            items_with_total_amount = [
                self.cart_item_service.get_cart_item_with_total_amount(item)
                for item in cart.items
            ]
            total_price = self.cart_service.get_total_price(items_with_total_amount)
            return ReadFullCartSchema(
                id=cart.id,
                items=items_with_total_amount,
                total_price=total_price,
                total_quantity=total_quantity,
            )
