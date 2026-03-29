from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.cart_items import CreateCartItemSchema, ReadCartItemWithTotalPriceSchema
from app.schemas.carts import ReadFullCartSchema
from app.services.cart_items import AbstractCartItemService
from app.services.carts import AbstractCartService
from app.utils.unit_of_work import AbstractUnitOfWork


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
                    await self.cart_item_service.increase_cart_item_quantity(
                        cart_item_id=existing_item.id,
                        quantity=session_item.quantity,
                        cart_id=user_cart.id,
                        uow=uow,
                    )
                    existing_item.quantity += session_item.quantity

                else:
                    new_cart_item = await self.cart_item_service.create(
                        item_in=CreateCartItemSchema(
                            cart_id=user_cart.id,
                            quantity=session_item.quantity,
                            product_id=session_item.product.id,
                        ),
                        uow=uow,
                    )
                    user_cart.items.append(
                        ReadCartItemWithTotalPriceSchema(
                            **session_item.model_dump(
                                exclude={"id"},
                            ),
                            id=new_cart_item.id,
                        ),
                    )

                user_cart.total_quantity += session_item.quantity
                user_cart.total_price += session_item.total_price

            await self.cart_service.delete(id=session_cart.id, uow=uow)

            return user_cart
