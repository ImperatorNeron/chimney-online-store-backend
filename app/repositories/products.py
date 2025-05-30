import logging
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy import desc, distinct, func, or_, Result, Select, select
from sqlalchemy.orm import aliased, selectinload

from app.core.exceptions.common import ItemNotFoundException, RepositoryException
from app.models.categories import Category
from app.models.orders import OrderItem
from app.models.products import ProductVariation, UniqueProduct
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import ReadPreviewProductSchema, ReadProductVariationSchema
from app.utils.sql_repository import BaseRepository


logger = logging.getLogger(__name__)


class VariationProductRepository(BaseRepository):
    """Repository for performing CRUD operations on ProductVariation data."""

    model = ProductVariation
    default_preload = [selectinload(model.product).selectinload(UniqueProduct.images)]
    default_order = [model.id]
    filter_characteristics = ["diameter", "length", "thickness", "angle", "metal_type"]

    async def bulk_create(self, data_list: list) -> list:
        instances = [self.model(**data.model_dump()) for data in data_list]
        self.session.add_all(instances)
        await self.session.flush(instances)
        return [instance.to_read_base_model() for instance in instances]

    async def update(self, id: int, item_in: BaseModel):  # noqa
        instance = await self._get_model(id=id)
        try:
            for field, value in item_in.model_dump(exclude_unset=True).items():
                setattr(instance, field, value)
            await self.session.flush([instance])
            await self.session.refresh(instance)
            return instance.to_read_base_model()
        except Exception as e:
            logger.error("Failed to update product: %s", e, exc_info=True)
            raise RepositoryException()

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

    async def all(  # noqa
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ) -> list[ReadProductVariationSchema]:
        models = await self._all_models(
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            options=options,
        )
        return [model.to_read_base_model() for model in models]

    async def count_filtered(self, filters: Optional[ProductFiltersSchema]) -> int:
        query = select(func.count()).select_from(self.model)
        query = self._apply_custom_filters(query=query, filters=filters)
        return (await self.session.execute(query)).scalar_one()

    async def fetch_filters(
        self,
        filters: Optional[ProductFiltersSchema],
    ):
        agg_cols = [
            func.array_agg(distinct(getattr(ProductVariation, attr))).label(attr)
            for attr in self.filter_characteristics
        ]
        query = select(*agg_cols)
        query = self._apply_custom_filters(query=query, filters=filters)
        result = await self.session.execute(query)
        row = result.one()
        return {
            attr: list(getattr(row, attr) or []) for attr in self.filter_characteristics
        }

    async def get_min_max_price(
        self,
        filters: Optional[ProductFiltersSchema],
    ) -> dict[str, float | None]:
        discounted_price = self.model.price * (1 - self.model.discount_percentage / 100)

        query = select(
            func.min(discounted_price).label("min_price"),
            func.max(discounted_price).label("max_price"),
        )

        query = self._apply_custom_filters(query=query, filters=filters)

        result = await self.session.execute(query)
        min_price, max_price = result.one()

        return {
            "min_price": round(min_price, 2) if min_price is not None else 0,
            "max_price": round(max_price, 2) if max_price is not None else 0,
        }

    async def list_products_by_ids(self, ids: list[int]):
        query = (
            select(self.model)
            .options(*self.default_preload)
            .where(self.model.id.in_(ids))
        )
        results: Result = await self.session.execute(query)
        products = results.scalars().all()
        return [product.to_read_model_with_preview() for product in products]

    async def get_with_most_orders(self, pagination_in: Optional[PaginationIn]):
        final_price_expr = self.model.price * (1 - self.model.discount_percentage / 100)
        query = select(self.model).options(*self.default_preload)
        query = query.add_columns(final_price_expr.label("final_price"))
        query = query.outerjoin(OrderItem, OrderItem.product_id == self.model.id)
        query = query.group_by(self.model.id)
        query = query.order_by(desc(func.count(OrderItem.id)))
        query = query.limit(pagination_in.limit).offset(pagination_in.offset)
        result = await self.session.execute(query)
        products = result.scalars().all()
        return [product.to_read_model_with_preview() for product in products]

    async def get(
        self,
        options: Optional[list] = None,
        **filters: Any,
    ) -> BaseModel:
        instance = await self._get_model(options=options, **filters)
        return instance.to_read_base_model()

    def _apply_custom_filters(
        self,
        query: Select,
        filters: Optional[ProductFiltersSchema],
    ) -> Select:

        if not filters:
            return query

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

        if filters.min_price and filters.max_price:
            discounted_price = self.model.price * (
                1 - self.model.discount_percentage / 100
            )
            query = query.where(
                discounted_price.between(filters.min_price, filters.max_price),
            )

        for attr in self.filter_characteristics:
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
