from typing import Optional

from sqlalchemy import Result, select
from sqlalchemy.orm import selectinload

from app.core.exceptions.common import ItemNotFoundException
from app.models.categories import Category
from app.models.products import Product
from app.schemas.products import CreateProductSchema, ReadPreviewProductSchema
from app.utils.sql_repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on Product data."""

    model = Product

    # TODO: refactor raise_if_exists. Need except IntegrityError and parse it or just do it for one slug
    # The problem is Race Conditions
    # The same problem in check_existance

    async def create(self, item_in: CreateProductSchema):
        await self.raise_if_exists({"slug": item_in.slug})
        category = await self.session.get(Category, item_in.category_id)

        if not category:
            raise ItemNotFoundException(model=Category, item_id=item_in.category_id)
        return await super().create(item_in=item_in)

    async def fetch_full_one_by_id(
        self,
        product_id: int,
    ):
        await self.raise_if_not_exists(item_id=product_id)

        stmt = (
            select(self.model)
            .options(selectinload(self.model.images))
            .where(self.model.id == product_id)
        )

        result: Result = await self.session.execute(stmt)
        product = result.scalars().first()
        return product.to_read_full_model()

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
