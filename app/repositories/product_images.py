from sqlalchemy import insert

from app.models.product_images import ProductImage
from app.schemas.product_images import ProductImageCreate
from app.utils.sql_repository import SQLAlchemyRepository


class ProductImageRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on ProductImages data."""

    model = ProductImage

    async def bulk_add(self, images: list[ProductImageCreate]):
        stmt = insert(ProductImage).values(images)
        await self.session.execute(stmt)
