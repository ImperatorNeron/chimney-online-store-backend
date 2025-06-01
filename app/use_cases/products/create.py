import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi_cache import FastAPICache

from app.core.constants import CACHED_PRODUCT_KEYS
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import ProductCreationException
from app.schemas.product_images import CreateProductImageSchema
from app.schemas.products import BaseCreateProductVariationSchema, CreateUniqueProductSchema, ReadAbsoluteProductSchema
from app.services.files import AbstractFileUploadService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractCreateProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_in: CreateUniqueProductSchema,
        variations_in: list[BaseCreateProductVariationSchema],
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema: ...


@dataclass
class CreateProductUseCase(AbstractCreateProductUseCase):

    product_service: AbstractProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileUploadService

    async def execute(
        self,
        product_in: CreateUniqueProductSchema,
        variations_in: list[BaseCreateProductVariationSchema],
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema:
        async with uow:
            image_data = []

            unique_product = await self.product_service.create_unique(
                product_in=product_in,
                uow=uow,
            )

            try:
                for img in images:
                    await self.file_service.verify_file(img)
                    metadata = self.file_service.get_metadata(img)
                    await self.file_service.bwrite_file(img, metadata["path"])
                    image_data.append(
                        CreateProductImageSchema(
                            file_path=metadata["path"],
                            alt=unique_product.name,
                            product_id=unique_product.id,
                        ),
                    )
                new_images = await self.product_image_service.bulk_create(
                    images=image_data,
                    uow=uow,
                )
            except BaseAppException:
                await self.file_service.cleanup_files(image_data)
                raise
            except Exception as e:
                logger.error("Failed to create product: %s", e, exc_info=True)
                await self.file_service.cleanup_files(image_data)
                raise ProductCreationException()

            product_variations = await self.product_service.create_variations(
                unique_product_id=unique_product.id,
                products_in=variations_in,
                uow=uow,
            )
            for key in CACHED_PRODUCT_KEYS:
                await FastAPICache.get_backend().set(key, None, expire=1)

            CACHED_PRODUCT_KEYS.clear()
            return ReadAbsoluteProductSchema(
                **unique_product.model_dump(),
                images=new_images,
                variations=product_variations,
            )


@dataclass
class CreateProductWithSupabaseUseCase(AbstractCreateProductUseCase):

    product_service: AbstractProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileUploadService

    async def execute(
        self,
        product_in: CreateUniqueProductSchema,
        variations_in: list[BaseCreateProductVariationSchema],
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema:
        async with uow:
            image_data = []

            unique_product = await self.product_service.create_unique(
                product_in=product_in,
                uow=uow,
            )

            try:
                for img in images:
                    await self.file_service.verify_file(img)
                    path = await self.file_service.write_to_supabase(file=img, unique_product_slug=unique_product.slug)
                    image_data.append(
                        CreateProductImageSchema(
                            file_path=path,
                            alt=unique_product.name,
                            product_id=unique_product.id,
                        ),
                    )
                new_images = await self.product_image_service.bulk_create(
                    images=image_data,
                    uow=uow,
                )
            except BaseAppException:
                await self.file_service.delete_from_supabase(image_data)
                raise
            except Exception as e:
                logger.error("Failed to create product: %s", e, exc_info=True)
                await self.file_service.delete_from_supabase(image_data)
                raise ProductCreationException()

            product_variations = await self.product_service.create_variations(
                unique_product_id=unique_product.id,
                products_in=variations_in,
                uow=uow,
            )
            for key in CACHED_PRODUCT_KEYS:
                await FastAPICache.get_backend().set(key, None, expire=1)

            CACHED_PRODUCT_KEYS.clear()
            return ReadAbsoluteProductSchema(
                **unique_product.model_dump(),
                images=new_images,
                variations=product_variations,
            )
