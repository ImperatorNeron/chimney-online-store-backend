from abc import abstractmethod
from typing import Callable, Type

from app.core.exceptions.common import ForeignKeyConstraintViolationException, ItemNotFoundException
from app.mappers.carts import CartItemCreateMapper, CartItemReadMapper
from app.schemas.cart_items import CreateCartItemSchema, ReadCartItemSchema
from app.services.base import AbstractCreate, AbstractDelete, Create, Delete
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCartItemService(
    AbstractCreate[ReadCartItemSchema, CreateCartItemSchema],
    AbstractDelete,
):

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


class CartItemService(
    AbstractCartItemService,
    Create[ReadCartItemSchema, CreateCartItemSchema],
    Delete,
):

    repository_name: str = "cart_item"
    read_mapper: Type[CartItemReadMapper] = CartItemReadMapper
    read_create_mapper: Type[CartItemReadMapper] = CartItemReadMapper
    create_mapper: Type[CartItemCreateMapper] = CartItemCreateMapper

    async def increase_cart_item_quantity(
        self,
        quantity: int,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        return await self._change_cart_item_quantity(
            quantity=quantity,
            cart_item_id=cart_item_id,
            cart_id=cart_id,
            uow=uow,
            action=uow.cart_item.increase_quantity,
        )

    async def decrease_cart_item_quantity(
        self,
        quantity: int,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:
        return await self._change_cart_item_quantity(
            quantity=quantity,
            cart_item_id=cart_item_id,
            cart_id=cart_id,
            uow=uow,
            action=uow.cart_item.decrease_quantity,
        )

    async def create(
        self,
        item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadCartItemSchema:

        await self._validate(cart_item_in=item_in, uow=uow)

        if await uow.cart_item.exists(
            cart_id=item_in.cart_id,
            product_id=item_in.product_id,
        ):
            cart_item = await uow.cart_item.get(
                cart_id=item_in.cart_id,
                product_id=item_in.product_id,
            )
            return await self.increase_cart_item_quantity(
                quantity=item_in.quantity,
                cart_item_id=cart_item.id,
                cart_id=item_in.cart_id,
                uow=uow,
            )

        return await super().create(item_in=item_in, uow=uow)

    async def _validate(
        self,
        cart_item_in: CreateCartItemSchema,
        uow: AbstractUnitOfWork,
    ):
        if not await uow.cart.exists(id=cart_item_in.cart_id):
            raise ForeignKeyConstraintViolationException(
                {"cart_id": "Корзина не існує."},
            )
        if not await uow.products.exists(id=cart_item_in.product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукт не існує."},
            )

    async def _change_cart_item_quantity(
        self,
        quantity: int,
        cart_item_id: int,
        cart_id: int,
        uow: AbstractUnitOfWork,
        action: Callable,
    ) -> ReadCartItemSchema:
        if not await uow.cart_item.exists(id=cart_item_id, cart_id=cart_id):
            raise ItemNotFoundException()

        cart_item = await action(
            quantity=quantity,
            cart_item_id=cart_item_id,
        )

        return self.read_mapper.to_dto(cart_item)
