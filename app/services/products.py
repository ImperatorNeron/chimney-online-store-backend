from abc import abstractmethod
from typing import Optional, Type

from app.core.exceptions.common import ForeignKeyConstraintViolationException
from app.mappers.products import (
    BaseProductVariationReadMapper,
    PreviewProductVariationReadMapper,
    PriceRangeReadMapper,
    ProductFiltersReadMapper,
    ProductVariationCreateMapper,
    ProductVariationUpdateMapper,
)
from app.schemas.filters import FiltersSchema, PaginationIn, PriceRangeSchema, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import (
    BaseUpdateVariationSchema,
    CreateProductVariationSchema,
    ReadPreviewProductSchema,
    ReadProductVariationSchema,
)
from app.services.base import (
    AbstractCount,
    AbstractCreate,
    AbstractDelete,
    AbstractRead,
    AbstractUpdate,
    Count,
    Create,
    Delete,
    Read,
    Update,
)
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductService(
    AbstractRead[ReadPreviewProductSchema],
    AbstractCount,
    AbstractCreate[ReadProductVariationSchema, CreateProductVariationSchema],
    AbstractUpdate[ReadProductVariationSchema, BaseUpdateVariationSchema],
    AbstractDelete,
):

    # Read =========================================
    @abstractmethod
    async def list_product_previews(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: Optional[SortOrderSchema],
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def get_filters(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> FiltersSchema: ...

    @abstractmethod
    async def get_min_max_price(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> list: ...

    @abstractmethod
    async def get_product_variations(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]: ...

    @abstractmethod
    async def get_popular_products(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]: ...


class ProductService(
    Read[ReadPreviewProductSchema],
    Count,
    AbstractProductService,
    Create[ReadProductVariationSchema, CreateProductVariationSchema],
    Update[ReadProductVariationSchema, BaseUpdateVariationSchema],
    Delete,
):
    read_mapper: Type[PreviewProductVariationReadMapper] = (
        PreviewProductVariationReadMapper
    )
    create_mapper: Type[ProductVariationCreateMapper] = ProductVariationCreateMapper
    update_mapper: Type[ProductVariationUpdateMapper] = ProductVariationUpdateMapper
    read_create_mapper: Type[BaseProductVariationReadMapper] = (
        BaseProductVariationReadMapper
    )
    read_update_mapper: Type[BaseProductVariationReadMapper] = (
        BaseProductVariationReadMapper
    )
    repository_name: str = "products"

    async def list_product_previews(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: Optional[SortOrderSchema],
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]:
        return self.read_mapper.to_dto_list(
            await uow.products.list_product_previews(
                pagination_in=pagination_in,
                filters=filters,
                sort_params=sort_params,
            ),
        )

    async def get_filters(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> FiltersSchema:
        return ProductFiltersReadMapper.to_dto(
            await uow.products.fetch_filters(filters=filters),
        )

    async def get_min_max_price(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> PriceRangeSchema:
        return PriceRangeReadMapper.to_dto(
            await uow.products.get_min_max_price(filters=filters),
        )

    async def get_product_variations(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]:
        self._get_product_variants_validation(product_id=product_id, uow=uow)
        # Just use to not write the same type
        return self.read_create_mapper.to_dto_list(
            await uow.products.all(filters={"product_id": product_id}),
        )

    async def get_popular_products(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]:
        return PreviewProductVariationReadMapper.to_dto_list(
            await uow.products.get_products_with_most_orders(
                pagination_in=pagination_in,
            ),
        )

    async def _bulk_create_validation(
        self, items_in: list[CreateProductVariationSchema], uow: AbstractUnitOfWork,
    ):
        if not await uow.unique_products.exists(id=items_in[0].product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
            )

    async def _get_product_variants_validation(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ):
        if not await uow.unique_products.exists(id=product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
