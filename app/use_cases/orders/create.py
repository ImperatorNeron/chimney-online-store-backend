from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.core.exceptions.common import EmptyCartException
from app.schemas.carts import ReadFullCartSchema
from app.schemas.orders import CreateOrderItemSchema, CreateOrderSchema, CreateOrderWithUserSchema, ReadOrderBaseSchema
from app.services.carts import AbstractCartService
from app.services.orders import AbstractOrderService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateOrderUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        order_in: CreateOrderSchema,
        cart: ReadFullCartSchema,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadOrderBaseSchema: ...


@dataclass
class CreateOrderUseCase(AbstractCreateOrderUseCase):
    order_service: AbstractOrderService
    cart_service: AbstractCartService

    async def execute(
        self,
        order_in: CreateOrderSchema,
        cart: ReadFullCartSchema,
        user_id: Optional[int],
        uow: AbstractUnitOfWork,
    ) -> ReadOrderBaseSchema:
        async with uow:

            if not cart.items:
                raise EmptyCartException()

            new_order_in = CreateOrderWithUserSchema(
                **order_in.model_dump(),
                user_id=user_id,
            )
            order = await self.order_service.create(order_in=new_order_in, uow=uow)
            await self.order_service.bulk_create(
                items=[
                    CreateOrderItemSchema(
                        order_id=order.id,
                        product_id=k.product.id,
                        quantity=k.quantity,
                        price_at_order=k.total_price,
                    )
                    for k in cart.items
                ],
                uow=uow,
            )
            await self.cart_service.delete_cart(cart_id=cart.id, uow=uow)
            return order
