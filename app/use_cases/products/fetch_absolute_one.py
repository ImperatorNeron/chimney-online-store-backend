import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi_cache import FastAPICache

from app.core.settings import settings
from app.schemas.products import ReadAbsoluteProductSchema
from app.services.categories import AbstractCategoryService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchAbsoluteProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema: ...


@dataclass
class FetchAbsoluteProductUseCase(ABC):

    product_service: AbstractProductService
    product_image_service: AbstractProductImageService
    category_service: AbstractCategoryService

    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema:
        key = f"product:{hashlib.sha256(product_slug.encode()).hexdigest()}"
        cached = await FastAPICache.get_backend().get(key)
        if cached:
            return ReadAbsoluteProductSchema.model_validate_json(cached)

        async with uow:
            unique_product = await self.product_service.get_unique_product(
                slug=product_slug,
                uow=uow,
            )
            images = await self.product_image_service.get_images(
                product_id=unique_product.id,
                uow=uow,
            )
            variations = await self.product_service.get_product_variations(
                product_id=unique_product.id,
                uow=uow,
            )
            categories = await self.category_service.get_category_hierarchy(
                category_id=unique_product.category_id,
                uow=uow,
            )
            result = ReadAbsoluteProductSchema(
                **unique_product.model_dump(),
                images=images,
                variations=variations,
                categories=categories,
            )

        await FastAPICache.get_backend().set(
            key,
            result.model_dump_json(),
            expire=settings.cache.expire,
        )
        return result
