from abc import ABC, abstractmethod

from app.core.exceptions.common import ForeignKeyConstraintViolationException, ItemNotFoundException
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
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema: ...

    @abstractmethod
    async def decrease_cart_item_quantity(
        self,
        quantity: int,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema: ...

    @abstractmethod
    async def create_cart_item(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema: ...

    @abstractmethod
    async def delete_cart_item(
        self,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


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
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        if not await uow.cart_item.exists(id=cart_item_id, cart_id=cart_id):
            raise ItemNotFoundException()
        return await uow.cart_item.increase_quantity(
            quantity=quantity,
            cart_item_id=cart_item_id,
        )

    async def decrease_cart_item_quantity(
        self,
        quantity: int,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        if not await uow.cart_item.exists(id=cart_item_id, cart_id=cart_id):
            raise ItemNotFoundException()
        return await uow.cart_item.decrease_quantity(
            quantity=quantity,
            cart_item_id=cart_item_id,
        )

    async def create_cart_item(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        if not await uow.cart.exists(id=cart_item_in.cart_id):
            raise ForeignKeyConstraintViolationException(
                {"cart_id": "Корзина не існує."},
            )
        if not await uow.products.exists(id=cart_item_in.product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукт не існує."},
            )
        if await uow.cart_item.exists(
            cart_id=cart_item_in.cart_id,
            product_id=cart_item_in.product_id,
        ):
            cart_item = await uow.cart_item.get(
                cart_id=cart_item_in.cart_id,
                product_id=cart_item_in.product_id,
            )
            return await self.increase_cart_item_quantity(
                quantity=cart_item_in.quantity,
                cart_item_id=cart_item.id,
                cart_id=cart_item_in.cart_id,
                uow=uow,
            )

        return await uow.cart_item.create(item_in=cart_item_in)

    async def delete_cart_item(
        self,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        await uow.cart_item.delete(id=cart_item_id, cart_id=cart_id)
