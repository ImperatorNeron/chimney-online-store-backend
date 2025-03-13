from typing import Optional

from sqlalchemy import Result, select
from sqlalchemy.orm import selectinload

from app.models.products import Product
from app.schemas.products import ReadPreviewProductSchema
from app.utils.sql_repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on Product data."""

    model = Product

    async def fetch_all_with_preview(
        self,
        pagination_in: Optional[ReadPreviewProductSchema] = None,
    ) -> list[ReadPreviewProductSchema]:
        stmt = (
            select(self.model)
            .options(selectinload(self.model.images))
            .order_by(self.model.id)
        )

        if pagination_in is not None:
            stmt = stmt.limit(pagination_in.limit).offset(pagination_in.offset)

        result: Result = await self.session.execute(stmt)

        return [
            product.to_read_model_with_preview()
            for product in list(result.scalars().all())
        ]
