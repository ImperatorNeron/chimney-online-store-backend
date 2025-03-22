from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions.common import ItemNotFoundException
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.products import Product
from app.utils.sql_repository import SQLAlchemyRepository


class CartRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on Carts data."""

    model = Cart

    async def fetch_with_full_item(self, **kwargs: dict):
        [(key, value)] = kwargs.items()
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(self.model.items)
                .selectinload(CartItem.product)
                .selectinload(Product.images),
            )
            .where(getattr(self.model, key) == value),
        )
        cart = result.scalars().all()

        if not len(cart):
            raise ItemNotFoundException(self.model, **kwargs)

        return cart[0].to_read_model_with_items()
