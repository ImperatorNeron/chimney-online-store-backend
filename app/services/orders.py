from abc import ABC, abstractmethod

from app.schemas.orders import (
    CreateOrderItemSchema,
    CreateOrderSchema,
    ReadOrderBaseSchema,
    ReadOrderItemBaseSchema,
    ReadOrderItemSchema,
    ReadOrderSchema,
)
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractOrderService(ABC):

    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderSchema]: ...

    @abstractmethod
    async def get_order_history(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderSchema]: ...

    @abstractmethod
    async def get_active_orders(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderSchema]: ...

    @abstractmethod
    async def get_total_price(
        self,
        order_items: list[ReadOrderItemSchema],
        price_discount: float,
    ) -> float: ...

    @abstractmethod
    async def get_total_quantity(
        self,
        order_items: list[ReadOrderItemSchema],
    ) -> int: ...

    @abstractmethod
    async def create(
        self,
        order_in: CreateOrderSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadOrderBaseSchema: ...

    @abstractmethod
    async def bulk_create(
        self,
        cart_items: list[CreateOrderItemSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderItemBaseSchema]: ...


class OrderService(AbstractOrderService):

    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderSchema]:
        return await uow.order.all()

    async def get_order_history(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderSchema]:
        return await uow.order.finished_orders_by_user_id(user_id=user_id)

    async def get_active_orders(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderSchema]:
        return await uow.order.current_orders_by_user_id(user_id=user_id)

    async def get_total_price(
        self,
        order_items: list[ReadOrderItemSchema],
        price_discount: float,
    ) -> float:
        return round(
            sum(item.price_at_order for item in order_items) - price_discount,
            2,
        )

    async def get_total_quantity(
        self,
        order_items: list[ReadOrderItemSchema],
    ) -> int:
        return sum(item.quantity for item in order_items)

    async def create(
        self,
        order_in: CreateOrderSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadOrderBaseSchema:
        return await uow.order.create(order_in=order_in)

    async def bulk_create(
        self,
        items: list[CreateOrderItemSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadOrderItemBaseSchema]:
        return await uow.order_item.bulk_create(data_list=items)
