from typing import Optional

from sqlalchemy import func, or_, Select, select
from sqlalchemy.orm import aliased, selectinload

from app.core.exceptions.common import ItemNotFoundException
from app.models.categories import Category
from app.models.products import ProductVariation, UniqueProduct
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import ReadPreviewProductSchema
from app.utils.sql_repository import BaseRepository


class ProductRepository(BaseRepository):
    """Repository for performing CRUD operations on ProductVariation data."""

    model = ProductVariation
    default_preload = [selectinload(model.product).selectinload(UniqueProduct.images)]
    default_order = [model.id]

    async def get_full(
        self,
        product_slug: str,
        product_variation_id: int,
    ):
        query = select(self.model)

        if self.default_preload:
            query = query.options(*self.default_preload)

        query = query.where(
            self.model.id == product_variation_id,
            self.model.product.has(UniqueProduct.slug == product_slug),
        )

        result = await self.session.execute(query)
        product_variation = result.scalars().first()

        if not product_variation:
            raise ItemNotFoundException()

        return product_variation.to_read_full_model()

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
                category_tree,
                category.parent_id == category_tree.c.id,
            )

            category_tree = category_tree.union_all(child_categories)

            query = query.join(self.model.product).join(UniqueProduct.category)
            query = query.where(Category.id.in_(select(category_tree.c.id)))

        if filters.text and not filters.category_slug:
            search_terms = filters.text.split()
            conditions = []
            for term in search_terms:
                if term.isdigit():
                    conditions.append(self.model.id == int(term))

                conditions.extend(
                    [
                        func.similarity(UniqueProduct.name, term) >= 0.05,
                        func.similarity(UniqueProduct.description, term) >= 0.05,
                    ],
                )

            query = query.join(self.model.product)
            query = query.where(or_(*conditions))

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
        product_variations = result.scalars().all()
        return [product.to_read_model_with_preview() for product in product_variations]

    async def count(self, filters: Optional[ProductFiltersSchema]) -> int:
        query = select(func.count()).select_from(self.model)
        query = self._apply_custom_filters(query=query, filters=filters)
        return (await self.session.execute(query)).scalar_one()
