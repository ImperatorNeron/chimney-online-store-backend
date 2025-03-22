from sqlalchemy import Result, update

from app.models.cart_item import CartItem
from app.utils.sql_repository import SQLAlchemyRepository


class CartItemRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on CartItem data."""

    model = CartItem

    async def increase_quantity(self, quantity: int, cart_item_id: int):
        result: Result = await self.session.execute(
            update(self.model)
            .where(self.model.id == cart_item_id)
            .values(quantity=CartItem.quantity + quantity)
            .returning(self.model),
        )
        updated = result.scalars().first()
        return updated.to_read_model()
