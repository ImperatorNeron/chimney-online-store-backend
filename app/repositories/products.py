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

    # dimension/attribute fields searched for numeric terms
    _numeric_attr_fields = ("diameter", "length", "thickness", "angle")

    @staticmethod
    def _is_numeric_term(term: str) -> bool:
        """True for integer or decimal terms: 800, 0.5, 1,0, 45.0."""
        return term.replace(",", ".").replace(".", "", 1).isdigit()

    @classmethod
    def _attr_conditions(cls, term, _index):
        """Extra search conditions matching a term against variation
        attributes.

        - numeric terms (integer OR decimal: "800", "0.5", "1,0") match the
          dimension fields diameter/length/thickness/angle. Both the raw term
          and a "N.0" normalized form are tried, because values are stored in
          mixed formats (e.g. length "0.5"/"1"/"1.0", angle "90.0", diameter
          "800/860"). A plain integer term also matches a variation id.
        - any term matches metal_type (so "нерж" hits "нержавіюча сталь").

        This lets a query like "труба 800 нерж" line up name↔труба,
        diameter↔800, metal_type↔нерж and rank as a full cross-field match.

        """
        conditions = [ProductVariation.metal_type.ilike(f"%{term}%")]

        if cls._is_numeric_term(term):
            norm = term.replace(",", ".")
            # candidate substrings to look for in the stored value
            needles = {norm}
            # match integer "1" against stored "1.0", and "1.0" against "1"
            if "." in norm:
                needles.add(norm.rstrip("0").rstrip("."))  # 1.0 -> 1
            else:
                needles.add(f"{norm}.0")                    # 1   -> 1.0
            for field in cls._numeric_attr_fields:
                col = getattr(ProductVariation, field)
                for needle in needles:
                    conditions.append(col.ilike(f"%{needle}%"))
            if term.isdigit():
                conditions.append(ProductVariation.id == int(term))

        return conditions

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
        # Count distinct PRODUCTS (one card per product), not variations.
        parsed = ProductFiltersSchema(**filters)
        query = select(func.count(distinct(self.model.product_id)))
        query = query.select_from(self.model)
        query = self._apply_custom_filters(query=query, filters=parsed)
        total = (await self.session.execute(query)).scalar_one()
        # For search, results are capped at the top 24, so report at most 24.
        is_search = bool(parsed.text and not parsed.category_slug)
        return min(total, 24) if is_search else total

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
                query, filters.text, self._attr_conditions,
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

        # Base filtered set of variations (relevance filter joins UniqueProduct).
        base = select(self.model.id.label("variation_id"))
        base = base.add_columns(self.model.product_id.label("product_id"))
        base = base.add_columns(final_price_expr.label("final_price"))
        base = self._apply_custom_filters(query=base, filters=filters)

        is_search = bool(filters and filters.text and not filters.category_slug)

        if is_search:
            main_rank, word_rank = self._build_relevance_score(
                filters.text, self._attr_conditions,
            )
            base = base.add_columns(
                main_rank.label("main_rank"),
                word_rank.label("word_rank"),
            )

        base = base.subquery("filtered")

        # Pick ONE representative variation per product (one card per product).
        # For search: the best-matching (lowest rank) variation of each product.
        # Otherwise: the cheapest variation as the representative.
        rep = select(base.c.variation_id)
        if is_search:
            rep = rep.distinct(base.c.product_id).order_by(
                base.c.product_id,
                base.c.main_rank.asc(),
                base.c.word_rank.asc(),
                base.c.final_price.asc(),
            )
        else:
            rep = rep.distinct(base.c.product_id).order_by(
                base.c.product_id,
                base.c.final_price.asc(),
            )
        rep_ids = rep.subquery("rep")

        # Final query: full variation rows for the chosen representatives only.
        query = select(self.model).options(*self.all_models_default_preload)
        query = query.add_columns(final_price_expr.label("final_price"))
        query = query.where(self.model.id.in_(select(rep_ids.c.variation_id)))

        # Order the resulting cards.
        if is_search:
            query = query.join(self.model.product)
            main_rank, word_rank = self._build_relevance_score(
                filters.text, self._attr_conditions,
            )
            query = query.order_by(main_rank.asc(), word_rank.asc())
        else:
            if sort_params.field == "final_price":
                order_field = final_price_expr
            else:
                order_field = getattr(self.model, sort_params.field)
            order_clause = order_field.asc() if sort_params.ordering == "asc" else order_field.desc()
            query = query.order_by(order_clause)

        # For search, cap results at the top 24 most-relevant cards.
        limit = min(pagination_in.limit, 24) if is_search else pagination_in.limit
        query = query.limit(limit).offset(pagination_in.offset)
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
