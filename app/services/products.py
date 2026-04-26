from abc import abstractmethod
from typing import Optional, Type

from app.core.exceptions.common import ForeignKeyConstraintViolationException
from app.mappers.products import (
    BaseProductVariationReadMapper,
    DiscountedAdminReadMapper,
    PreviewProductVariationReadMapper,
    PriceRangeReadMapper,
    ProductFiltersReadMapper,
    ProductVariationCreateMapper,
    ProductVariationUpdateMapper,
)
from app.schemas.filters import (
    FiltersSchema,
    PaginationIn,
    PriceRangeSchema,
    ProductFiltersSchema,
    SortOrderSchema,
    VariationFiltersSchema,
    VariationSortOrderSchema,
)
from app.schemas.products import (
    BaseUpdateVariationSchema,
    CreateProductVariationSchema,
    ReadDiscountedAdminSchema,
    ReadPreviewProductSchema,
    ReadProductVariationSchema,
)
from app.schemas.website_settings import ReadWebSiteSettingsSchema
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
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
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
        uow: AbstractUnitOfWork,
        product_id: int,
        filters: Optional[VariationFiltersSchema] = None,
        sort_params: Optional[VariationSortOrderSchema] = None,
        pagination_in: Optional[PaginationIn] = None,
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadProductVariationSchema]: ...

    @abstractmethod
    async def get_popular_products(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def get_discounted_products(
        self,
        uow: AbstractUnitOfWork,
        limit: int,
        offset: int,
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def get_discounted_admin(self, uow: AbstractUnitOfWork) -> list[ReadDiscountedAdminSchema]: ...

    @abstractmethod
    async def update_discount_sort_order(
        self, uow: AbstractUnitOfWork, variation_id: int, sort_order: int,
    ) -> None: ...


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
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadPreviewProductSchema]:
        return self.read_mapper.to_dto_list(
            await uow.products.list_product_previews(
                pagination_in=pagination_in,
                filters=filters,
                sort_params=sort_params,
            ),
            website_settings=website_settings,
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
        uow: AbstractUnitOfWork,
        product_id: int,
        filters: Optional[VariationFiltersSchema] = None,
        sort_params: Optional[VariationSortOrderSchema] = None,
        pagination_in: Optional[PaginationIn] = None,
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadProductVariationSchema]:
        await self._get_product_variants_validation(product_id=product_id, uow=uow)
        filters_dict = {"product_id": product_id}
        if filters is not None:
            filters_dict.update(filters.model_dump(exclude_none=True))
        return self.read_create_mapper.to_dto_list(
            await self._repository(uow).all(
                **self._prepare_list_params(filters=filters_dict, pagination_in=pagination_in, order_by=sort_params),
            ),
            website_settings=website_settings,
        )

    async def get_popular_products(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadPreviewProductSchema]:
        return PreviewProductVariationReadMapper.to_dto_list(
            await uow.products.get_products_with_most_orders(
                pagination_in=pagination_in,
            ),
            website_settings=website_settings,
        )

    async def get_discounted_products(
        self,
        uow: AbstractUnitOfWork,
        limit: int,
        offset: int,
        website_settings: Optional[ReadWebSiteSettingsSchema] = None,
    ) -> list[ReadPreviewProductSchema]:
        return PreviewProductVariationReadMapper.to_dto_list(
            await uow.products.get_discounted_products(limit=limit, offset=offset),
            website_settings=website_settings,
        )

    async def get_discounted_admin(self, uow: AbstractUnitOfWork) -> list[ReadDiscountedAdminSchema]:
        return DiscountedAdminReadMapper.to_dto_list(
            await self._repository(uow).get_discounted_admin(),
        )

    async def update_discount_sort_order(
        self, uow: AbstractUnitOfWork, variation_id: int, sort_order: int,
    ) -> None:
        await self._repository(uow).update_discount_sort_order(
            variation_id=variation_id, sort_order=sort_order,
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
        uow: AbstractUnitOfWork,
        product_id: int,
    ):
        if not await uow.unique_products.exists(id=product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
