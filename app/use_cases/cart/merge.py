from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.cart_items import CreateCartItemSchema, ReadCartItemWithTotalPriceSchema
from app.schemas.carts import ReadFullCartSchema
from app.services.cart_items import AbstractCartItemService
from app.services.carts import AbstractCartService
from app.utils.unit_of_work import AbstractUnitOfWork


MAX_QUANTITY_PER_ITEM = 100
MAX_UNIQUE_ITEMS = 100


class AbstractMergeCartsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        user_cart: ReadFullCartSchema,
        session_cart: ReadFullCartSchema,
    ) -> ReadFullCartSchema: ...


@dataclass
class MergeCartsUseCase(AbstractMergeCartsUseCase):

    cart_service: AbstractCartService
    cart_item_service: AbstractCartItemService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        user_cart: ReadFullCartSchema,
        session_cart: ReadFullCartSchema,
    ) -> ReadFullCartSchema:
        async with uow:
            for session_item in session_cart.items:
                existing_item = next(
                    (
                        i
                        for i in user_cart.items
                        if i.product.id == session_item.product.id
                    ),
                    None,
                )
                if existing_item:
                    add_qty = min(
                        session_item.quantity,
                        MAX_QUANTITY_PER_ITEM - existing_item.quantity,
                    )
                    if add_qty > 0:
                        await self.cart_item_service.increase_cart_item_quantity(
                            cart_item_id=existing_item.id,
                            quantity=add_qty,
                            cart_id=user_cart.id,
                            uow=uow,
                        )
                        existing_item.quantity += add_qty
                        existing_item.total_price = (
                            existing_item.quantity * existing_item.product.discount_price
                        )
                        user_cart.total_quantity += add_qty
                        user_cart.total_price += add_qty * session_item.product.discount_price
                else:
                    if len(user_cart.items) >= MAX_UNIQUE_ITEMS:
                        continue

                    capped_qty = min(session_item.quantity, MAX_QUANTITY_PER_ITEM)
                    new_cart_item = await self.cart_item_service.create(
                        item_in=CreateCartItemSchema(
                            cart_id=user_cart.id,
                            quantity=capped_qty,
                            product_id=session_item.product.id,
                        ),
                        uow=uow,
                    )
                    user_cart.items.append(
                        ReadCartItemWithTotalPriceSchema(
                            **session_item.model_dump(exclude={"id", "quantity", "total_price"}),
                            id=new_cart_item.id,
                            quantity=capped_qty,
                            total_price=capped_qty * session_item.product.discount_price,
                        ),
                    )
                    user_cart.total_quantity += capped_qty
                    user_cart.total_price += capped_qty * session_item.product.discount_price

            await self.cart_service.delete(id=session_cart.id, uow=uow)

            return user_cart
