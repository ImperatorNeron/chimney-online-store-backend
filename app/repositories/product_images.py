from sqlalchemy import delete

from app.models.product_images import ProductImage
from app.utils.sql_repository import BaseRepository


class ProductImageRepository(BaseRepository):
    """Repository for performing CRUD operations on ProductImages data."""

    model = ProductImage

    async def delete_by_ids(self, ids: list[int]):
        stmt = delete(ProductImage).where(ProductImage.id.in_(ids))
        await self.session.execute(stmt)
