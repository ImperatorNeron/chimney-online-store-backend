from typing import Optional

from sqlalchemy import func, Select, select
from sqlalchemy.orm import aliased, selectinload

from app.models.categories import Category
from app.models.products import Product
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import ReadPreviewProductSchema
from app.utils.sql_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Repository for performing CRUD operations on Product data."""

    model = Product
    default_preload = [selectinload(Product.images)]
    default_order = [Product.id]

    async def get_full(self, product_slug: str):
        product = await self._get_model(slug=product_slug, options=self.default_preload)
        return product.to_read_full_model()

    def _apply_custom_filters(
        self,
        query: Select,
        filters: Optional[ProductFiltersSchema],
    ) -> Select:
        if filters.category_slug:
            category = aliased(Category)

            category_tree = (
                select(Category.id)
                .where(Category.slug == filters.category_slug)
                .cte(name="category_tree", recursive=True)
            )

            child_categories = select(category.id).join(
                category_tree, category.parent_id == category_tree.c.id,
            )

            category_tree = category_tree.union_all(child_categories)

            query = query.join(Product.category).where(
                Category.id.in_(select(category_tree.c.id)),
            )
        return query

    def _build_query(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: SortOrderSchema,
        pagination_in: PaginationIn,
    ) -> Select:
        final_price_expr = self.model.price * (1 - self.model.discount_percentage / 100)
        query = select(self.model).options(*self.default_preload)
        query = query.add_columns(final_price_expr.label("final_price"))
        query = self._apply_custom_filters(query=query, filters=filters)

        if sort_params.field == "final_price":
            order_field = final_price_expr
        else:
            order_field = getattr(self.model, sort_params.field)

        if sort_params.ordering == "asc":
            order_clause = order_field.asc()
        else:
            order_clause = order_field.desc()

        query = query.order_by(order_clause)
        query = query.limit(pagination_in.limit).offset(pagination_in.offset)
        return query

    async def list_preview(
        self,
        pagination_in: Optional[PaginationIn],
        filters: Optional[ProductFiltersSchema],
        sort_params: SortOrderSchema,
    ) -> list[ReadPreviewProductSchema]:
        query = self._build_query(
            filters=filters,
            sort_params=sort_params,
            pagination_in=pagination_in,
        )
        result = await self.session.execute(query)
        products = result.scalars().all()
        return [product.to_read_model_with_preview() for product in products]

    async def count(self, filters: Optional[ProductFiltersSchema]) -> int:
        query = select(func.count()).select_from(self.model)
        query = self._apply_custom_filters(query=query, filters=filters)
        return (await self.session.execute(query)).scalar_one()
