import logging
from typing import Any, Optional

from sqlalchemy import case, desc, distinct, func, Select, select, Sequence
from sqlalchemy.orm import aliased, selectinload

from app.core import constants
from app.models.base import BaseModel as Model
from app.models.categories import Category
from app.models.orders import OrderItem
from app.models.products import ProductVariation, UniqueProduct
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import ReadPreviewProductSchema
from app.utils.search_mixin import RelevanceSearchMixin
from app.utils.sql_repository import BaseRepository


logger = logging.getLogger(__name__)


class VariationProductRepository(RelevanceSearchMixin, BaseRepository):
    """Repository for performing CRUD operations on ProductVariation data."""

    model = ProductVariation
    all_models_default_preload = [selectinload(model.product).selectinload(UniqueProduct.images)]
    search_ilike_fields = [UniqueProduct.name, UniqueProduct.description]
    search_similarity_fields = [UniqueProduct.name, UniqueProduct.description]
    search_similarity_threshold = 0.4

    @staticmethod
    def _digit_id_condition(term, _index):
        """Extra condition: match numeric terms as variation id."""
        if term.isdigit():
            return [ProductVariation.id == int(term)]
        return []

    async def list_product_previews(
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
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        query = select(func.count()).select_from(self.model)
        query = self._apply_custom_filters(
            query=query, filters=ProductFiltersSchema(**filters),
        )
        return (await self.session.execute(query)).scalar_one()

    async def fetch_filters(
        self,
        filters: Optional[ProductFiltersSchema],
    ) -> Model:
        agg_cols = [
            func.array_agg(distinct(getattr(ProductVariation, attr))).label(attr)
            for attr in constants.FILTERS
        ]
        query = select(*agg_cols)
        query = self._apply_custom_filters(query=query, filters=filters)
        result = await self.session.execute(query)
        return result.one()

    async def get_min_max_price(
        self,
        filters: Optional[ProductFiltersSchema],
    ) -> Model:
        discounted_price = self.model.price * (1 - self.model.discount_percentage / 100)

        query = select(
            func.min(discounted_price).label("min_price"),
            func.max(discounted_price).label("max_price"),
        )

        query = self._apply_custom_filters(query=query, filters=filters)

        result = await self.session.execute(query)
        return result.one()

    async def get_products_with_most_orders(
        self, pagination_in: Optional[PaginationIn],
    ) -> Sequence[Model]:
        final_price_expr = self.model.price * (1 - self.model.discount_percentage / 100)
        query = select(self.model).options(*self.all_models_default_preload)
        query = query.add_columns(final_price_expr.label("final_price"))
        query = query.outerjoin(OrderItem, OrderItem.product_id == self.model.id)
        query = query.group_by(self.model.id)
        query = query.order_by(desc(func.count(OrderItem.id)))
        query = query.limit(pagination_in.limit).offset(pagination_in.offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    def _apply_custom_filters(
        self,
        query: Select,
        filters: Optional[ProductFiltersSchema],
    ) -> Select:

        if not filters:
            return query

        if filters.product_id:
            query = query.where(self.model.product_id == filters.product_id)

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
            query = query.join(self.model.product)
            query = self._apply_relevance_filter(
                query, filters.text, self._digit_id_condition,
            )

        if filters.min_price and filters.max_price:
            discounted_price = self.model.price * (
                1 - self.model.discount_percentage / 100
            )
            query = query.where(
                discounted_price.between(filters.min_price, filters.max_price),
            )

        for attr in constants.FILTERS:
            value = getattr(filters, attr, None)
            if value:
                query = query.where(getattr(self.model, attr) == value)

        return query

    def _build_query(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: SortOrderSchema,
        pagination_in: PaginationIn,
    ) -> Select:
        final_price_expr = self.model.price * (1 - self.model.discount_percentage / 100)
        query = select(self.model).options(*self.all_models_default_preload)
        query = query.add_columns(final_price_expr.label("final_price"))
        query = self._apply_custom_filters(query=query, filters=filters)

        query = self._apply_relevance_ordering(query, self._digit_id_condition)

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

    async def get_discounted_products(self, limit: int, offset: int) -> Sequence:
        sort_expr = case(
            (self.model.discount_sort_order.isnot(None), self.model.discount_sort_order),
            else_=9999,
        )
        query = (
            select(self.model)
            .options(*self.all_models_default_preload)
            .where(self.model.discount_percentage > 0)
            .order_by(sort_expr, desc(self.model.discount_percentage))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_discounted_admin(self) -> Sequence:
        sort_expr = case(
            (self.model.discount_sort_order.isnot(None), self.model.discount_sort_order),
            else_=9999,
        )
        query = (
            select(
                self.model.id,
                self.model.price,
                self.model.discount_percentage,
                self.model.discount_sort_order,
                UniqueProduct.name,
                UniqueProduct.slug,
            )
            .join(UniqueProduct, self.model.product_id == UniqueProduct.id)
            .where(self.model.discount_percentage > 0)
            .order_by(sort_expr, desc(self.model.discount_percentage))
        )
        result = await self.session.execute(query)
        return result.all()

    async def update_discount_sort_order(self, variation_id: int, sort_order: int) -> None:
        instance = await self._get_model(id=variation_id)
        instance.discount_sort_order = sort_order
        await self.session.flush()

    async def fetch_variation_filters(self, product_id: int) -> Model:
        agg_cols = [
            func.array_agg(distinct(getattr(ProductVariation, attr))).label(attr)
            for attr in constants.FILTERS
        ]
        query = select(*agg_cols).where(self.model.product_id == product_id)
        result = await self.session.execute(query)
        return result.one()

    async def get_new_products(self, limit: int, offset: int) -> Sequence:
        query = (
            select(self.model)
            .options(*self.all_models_default_preload)
            .where(self.model.discount_percentage == 0)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
