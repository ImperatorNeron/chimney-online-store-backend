from sqlalchemy import insert, Result

from app.models.product_images import ProductImage
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.utils.sql_repository import SQLAlchemyRepository


class ProductImageRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on ProductImages data."""

    model = ProductImage

    async def bulk_add(
        self,
        images: list[CreateProductImageSchema],
    ) -> list[ReadProductImageSchema]:
        stmt = (
            insert(ProductImage)
            .values([image.model_dump() for image in images])
            .returning(ProductImage)
        )
        result: Result = await self.session.execute(stmt)
        return [img.to_read_model() for img in result.scalars().all()]
