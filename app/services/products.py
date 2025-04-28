from abc import ABC, abstractmethod
from typing import Optional

from app.core.exceptions.common import ForeignKeyConstraintViolationException, UniqueConstraintViolationsException
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import CreateProductSchema, ReadFullProductSchema, ReadPreviewProductSchema, ReadProductSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductService(ABC):

    @abstractmethod
    async def list_all(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: Optional[SortOrderSchema],
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def get_products_count(
        self,
        uow: AbstractUnitOfWork,
        filters: Optional[ProductFiltersSchema],
    ) -> int: ...

    @abstractmethod
    async def get_full_one(
        self,
        product_slug: str,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema: ...

    @abstractmethod
    async def create(
        self,
        product_in: CreateProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadProductSchema: ...


class ProductService(AbstractProductService):
    async def list_all(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: Optional[SortOrderSchema],
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]:
        return await uow.products.list_preview(
            pagination_in=pagination_in,
            filters=filters,
            sort_params=sort_params,
        )

    async def get_products_count(
        self,
        uow: AbstractUnitOfWork,
        filters: Optional[ProductFiltersSchema],
    ) -> int:
        return await uow.products.count(filters=filters)

    async def get_full_one(
        self,
        product_slug: str,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema:
        return await uow.products.get_full(
            product_slug=product_slug,
            product_variation_id=product_variation_id,
        )

    async def create(
        self,
        product_in: CreateProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadProductSchema:
        if await uow.products.exists(slug=product_in.slug):
            raise UniqueConstraintViolationsException(
                {"slug": "Продукт з цим url вже існує."},
            )
        if not await uow.categories.exists(id=product_in.category_id):
            raise ForeignKeyConstraintViolationException(
                {"category_id": "Категорія не існує."},
            )
        return await uow.products.create(item_in=product_in)
