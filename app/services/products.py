from abc import ABC, abstractmethod
from typing import Optional

from app.core.exceptions.common import (
    ForeignKeyConstraintViolationException,
    ItemNotFoundException,
    UniqueConstraintViolationsException,
)
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import (
    BaseCreateProductVariationSchema,
    BaseUpdateVariationSchema,
    CreateProductVariationSchema,
    CreateUniqueProductSchema,
    ReadFullProductSchema,
    ReadPreviewProductSchema,
    ReadProductVariationSchema,
    ReadUniqueProductSchema,
    UpdateUniqueProductSchema,
)
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductService(ABC):

    # Read =========================================
    @abstractmethod
    async def list_all(
        self,
        filters: Optional[ProductFiltersSchema],
        sort_params: Optional[SortOrderSchema],
        uow: AbstractUnitOfWork,
        pagination_in: Optional[PaginationIn],
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def list_all_unique(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadUniqueProductSchema]: ...

    @abstractmethod
    async def list_variations_by_product_id(
        self,
        unique_product_id: int,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]: ...

    @abstractmethod
    async def get_products_by_ids(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def get_products_count(
        self,
        uow: AbstractUnitOfWork,
        filters: Optional[ProductFiltersSchema],
    ) -> int: ...

    @abstractmethod
    async def get_unique_products_count(
        self,
        uow: AbstractUnitOfWork,
    ) -> int: ...

    @abstractmethod
    async def count_variations_by_product_id(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> int: ...

    @abstractmethod
    async def get_full_one(
        self,
        product_slug: str,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema: ...

    @abstractmethod
    async def get_filters(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> dict: ...

    @abstractmethod
    async def get_min_max_price(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> list: ...

    @abstractmethod
    async def get_unique_product(
        self,
        slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema: ...

    @abstractmethod
    async def get_product_variations(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]: ...

    # Create =========================================
    @abstractmethod
    async def create_unique(
        self,
        product_in: CreateUniqueProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema: ...

    @abstractmethod
    async def create_variations(
        self,
        unique_product_id: int,
        products_in: list[BaseCreateProductVariationSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]: ...

    # Update =========================================
    @abstractmethod
    async def update_unique(
        self,
        unique_product_id: int,
        product_in: UpdateUniqueProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema: ...

    @abstractmethod
    async def update_variation(
        self,
        variation_id: int,
        product_in: BaseUpdateVariationSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadProductVariationSchema: ...

    # Delete =========================================
    @abstractmethod
    async def delete_unique(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...

    @abstractmethod
    async def delete_variation(
        self,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


class ProductService(AbstractProductService):

    # Read =========================================
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

    async def list_all_unique(
        self,
        pagination_in: Optional[PaginationIn],
        uow: AbstractUnitOfWork,
    ) -> list[ReadUniqueProductSchema]:
        return await uow.unique_products.all(
            limit=pagination_in.limit,
            offset=pagination_in.offset,
        )

    async def list_variations_by_product_id(
        self,
        unique_product_id: int,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]:
        return await uow.products.all(
            filters={"product_id": unique_product_id},
            limit=pagination_in.limit,
            offset=pagination_in.offset,
        )

    async def get_products_by_ids(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadPreviewProductSchema]:
        return await uow.products.list_products_by_ids(ids=ids)

    async def get_products_count(
        self,
        uow: AbstractUnitOfWork,
        filters: Optional[ProductFiltersSchema],
    ) -> int:
        return await uow.products.count_filtered(filters=filters)

    async def get_unique_products_count(
        self,
        uow: AbstractUnitOfWork,
    ) -> int:
        return await uow.unique_products.count()

    async def count_variations_by_product_id(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> int:
        return await uow.products.count(product_id=unique_product_id)

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

    async def get_filters(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> dict:
        return await uow.products.fetch_filters(filters=filters)

    async def get_min_max_price(
        self,
        filters: ProductFiltersSchema,
        uow: AbstractUnitOfWork,
    ) -> list:
        return await uow.products.get_min_max_price(filters=filters)

    async def get_unique_product(
        self,
        slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema:
        if not await uow.unique_products.exists(slug=slug):
            raise ItemNotFoundException(
                {"slug": "Продукт з цим url не існує."},
                detail="Не існує продукту з даним slug",
            )
        return await uow.unique_products.get(slug=slug)

    async def get_product_variations(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]:
        if not await uow.unique_products.exists(id=product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
        return await uow.products.all(filters={"product_id": product_id})

    # Create =========================================
    async def create_unique(
        self,
        product_in: CreateUniqueProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema:
        if await uow.unique_products.exists(slug=product_in.slug):
            raise UniqueConstraintViolationsException(
                {"slug": "Продукт з цим url вже існує."},
                detail="Продукт з цим slug вже існує",
            )
        if not await uow.categories.exists(id=product_in.category_id):
            raise ForeignKeyConstraintViolationException(
                {"category_id": "Категорія не існує."},
                detail="Не існує даної категорії",
            )
        return await uow.unique_products.create(item_in=product_in)

    async def create_variations(
        self,
        unique_product_id: int,
        products_in: list[BaseCreateProductVariationSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductVariationSchema]:
        if not await uow.unique_products.exists(id=unique_product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
            )
        price_increase_percentage = 30
        updated_products = [
            CreateProductVariationSchema(
                **product.model_dump(exclude={"price"}),
                price=product.price * (1 + price_increase_percentage / 100),
                product_id=unique_product_id,
            )
            for product in products_in
        ]
        return await uow.products.bulk_create(data_list=updated_products)

    # Update =========================================
    async def update_unique(
        self,
        unique_product_id: int,
        product_in: UpdateUniqueProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema:
        return await uow.unique_products.update(
            id=unique_product_id,
            item_in=product_in,
        )

    async def update_variation(
        self,
        variation_id: int,
        product_in: BaseUpdateVariationSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadProductVariationSchema:
        return await uow.products.update(id=variation_id, item_in=product_in)

    # Delete =========================================
    async def delete_unique(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        await uow.unique_products.delete(id=unique_product_id)

    async def delete_variation(
        self,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        await uow.products.delete(id=product_variation_id)
