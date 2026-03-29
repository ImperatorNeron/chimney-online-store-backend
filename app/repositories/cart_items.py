from sqlalchemy import Result, update

from app.models.cart_item import CartItem
from app.utils.sql_repo import BaseRepository


class CartItemRepository(BaseRepository):
    """Repository for performing CRUD operations on CartItem data."""

    model = CartItem

    async def _adjust_quantity(self, cart_item_id: int, value_expr, condition) -> CartItem:
        result: Result = await self.session.execute(
            update(self.model)
            .where(self.model.id == cart_item_id)
            .where(condition)
            .values(quantity=value_expr)
            .returning(self.model),
        )
        if not (updated := result.scalars().first()):
            # TODO: add custom exception
            raise ValueError("Quantity out of allowed range or item not found")
        return updated

    async def increase_quantity(self, quantity: int, cart_item_id: int) -> CartItem:
        return await self._adjust_quantity(
            cart_item_id,
            CartItem.quantity + quantity,
            (CartItem.quantity + quantity <= 999),
        )

    async def decrease_quantity(self, quantity: int, cart_item_id: int) -> CartItem:
        return await self._adjust_quantity(
            cart_item_id,
            CartItem.quantity - quantity,
            (CartItem.quantity - quantity >= 1),
        )
