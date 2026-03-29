from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.products import ProductVariation, UniqueProduct
from app.utils.sql_repo import BaseRepository


class CartRepository(BaseRepository):
    """Repository for performing CRUD operations on Carts data."""

    model = Cart
    default_preload = [
        selectinload(Cart.items)
        .selectinload(CartItem.product)
        .selectinload(ProductVariation.product)
        .selectinload(UniqueProduct.images),
    ]

    async def get(self, **conditions) -> Cart:
        return await self._get_model(options=self.default_preload, **conditions)
