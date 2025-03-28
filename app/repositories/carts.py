from typing import Optional

from sqlalchemy.orm import selectinload

from app.core.exceptions.common import InvalidRequestParametersException
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.products import Product
from app.utils.sql_repository import BaseRepository


class CartRepository(BaseRepository):
    """Repository for performing CRUD operations on Carts data."""

    model = Cart
    default_preload = [
        selectinload(Cart.items)
        .selectinload(CartItem.product)
        .selectinload(Product.images),
    ]

    async def get_with_items(
        self,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ):
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        elif session_id:
            filters["session_id"] = session_id
        else:
            raise InvalidRequestParametersException(
                required_params=["user_id", "session_id"],
            )

        cart = await self._get_model(
            options=self.default_preload,
            **filters,
        )

        return cart.to_read_model_with_items()
