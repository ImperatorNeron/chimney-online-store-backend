from typing import Optional

from sqlalchemy.orm import selectinload

from app.models.products import Product
from app.schemas.filters import PaginationIn
from app.schemas.products import ReadPreviewProductSchema
from app.utils.sql_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Repository for performing CRUD operations on Product data."""

    model = Product
    default_preload = [selectinload(Product.images)]
    default_order = [Product.id]

    async def get_full(
        self,
        product_id: int,
    ):
        product = await self._get_model(
            id=product_id,
            options=self.default_preload,
        )
        return product.to_read_full_model()

    async def list_preview(
        self,
        pagination_in: Optional[PaginationIn] = None,
    ) -> list[ReadPreviewProductSchema]:
        products = await self._all_models(
            limit=pagination_in.limit,
            offset=pagination_in.offset,
            options=self.default_preload,
        )
        return [product.to_read_model_with_preview() for product in products]
