from abc import ABC, abstractmethod

from app.schemas.cart_items import (
    CreateCartItemSchema,
    ReadCartItemSchema,
    ReadCartItemWithProductSchema,
    ReadCartItemWithTotalPriceSchema,
)
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCartItemService(ABC):

    @abstractmethod
    def get_cart_item_with_total_amount(
        self,
        item: ReadCartItemWithProductSchema,
    ) -> ReadCartItemWithTotalPriceSchema: ...

    @abstractmethod
    async def increase_cart_item_quantity(
        self,
        cart_item_id: int,
        quantity: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema: ...

    @abstractmethod
    async def create_cart_item(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema: ...


class CartItemService(AbstractCartItemService):

    def get_cart_item_with_total_amount(
        self,
        item: ReadCartItemWithProductSchema,
    ) -> ReadCartItemWithTotalPriceSchema:
        return ReadCartItemWithTotalPriceSchema(
            **item.model_dump(),
            total_price=item.quantity * item.product.price,
        )

    async def increase_cart_item_quantity(
        self,
        quantity: int,
        cart_item_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        return await uow.cart_item.increase_quantity(
            quantity=quantity,
            cart_item_id=cart_item_id,
        )

    async def create_cart_item(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        return await uow.cart_item.create(item_in=cart_item_in)
