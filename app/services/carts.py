from abc import ABC, abstractmethod

from app.schemas.cart_items import ReadCartItemWithProductSchema, ReadCartItemWithTotalPriceSchema
from app.schemas.carts import CreateCartSchema, ReadCartSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCartService(ABC):
    @abstractmethod
    async def get_cart(
        self,
        uow: AbstractUnitOfWork,
        **kwargs: dict,
    ) -> ReadCartSchema: ...

    @abstractmethod
    def get_total_quantity(self, items: list[ReadCartItemWithProductSchema]) -> int: ...

    @abstractmethod
    def get_total_price(
        self,
        items: list[ReadCartItemWithTotalPriceSchema],
    ) -> float: ...

    @abstractmethod
    async def create_cart(
        self,
        uow: AbstractUnitOfWork,
        cart_in: CreateCartSchema,
    ) -> ReadCartSchema: ...

    @abstractmethod
    async def delete_cart(
        self,
        uow: AbstractUnitOfWork,
        cart_id: int,
    ) -> None: ...


class CartService(AbstractCartService):

    async def get_cart(
        self,
        uow: AbstractUnitOfWork,
        **kwargs: dict,
    ) -> ReadCartSchema:
        return await uow.cart.get_with_items(**kwargs)

    def get_total_quantity(self, items: list[ReadCartItemWithProductSchema]) -> int:
        return sum(item.quantity for item in items)

    def get_total_price(self, items: list[ReadCartItemWithTotalPriceSchema]) -> float:
        return sum(item.total_price for item in items)

    async def create_cart(
        self,
        uow: AbstractUnitOfWork,
        cart_in: CreateCartSchema,
    ) -> ReadCartSchema:
        return await uow.cart.create(item_in=cart_in)

    async def delete_cart(
        self,
        uow: AbstractUnitOfWork,
        cart_id: int,
    ) -> None:
        await uow.cart.delete(id=cart_id)
