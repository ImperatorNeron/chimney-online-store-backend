import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import UploadFile

from app.mappers.products import BaseProductVariationToProductVariationCreateMapper
from app.schemas.products import BaseCreateProductVariationSchema, CreateUniqueProductSchema, ReadAbsoluteProductSchema
from app.services.files import AbstractFileStorageService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.services.unique_products import AbstractUniqueProductService
from app.use_cases.products._shared import invalidate_products_cache, upload_and_create_product_images
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractCreateProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_in: CreateUniqueProductSchema,
        variations_in: list[BaseCreateProductVariationSchema],
        images: list[UploadFile],
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema: ...


@dataclass
class CreateProductUseCase(AbstractCreateProductUseCase):
    product_service: AbstractProductService
    unique_product_service: AbstractUniqueProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileStorageService

    async def execute(
        self,
        product_in: CreateUniqueProductSchema,
        variations_in: list[BaseCreateProductVariationSchema],
        images: list[UploadFile],
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema:
        async with uow:
            unique_product = await self.unique_product_service.create(
                item_in=product_in,
                uow=uow,
            )

            new_images = await upload_and_create_product_images(
                images=images,
                product_id=unique_product.id,
                product_slug=unique_product.slug,
                alt=unique_product.name,
                file_service=self.file_service,
                product_image_service=self.product_image_service,
                uow=uow,
                logger=logger,
                log_error_message="Failed to create product: %s",
            )

            product_variations = await self.product_service.bulk_create(
                items_in=BaseProductVariationToProductVariationCreateMapper.to_dto_list(
                    variations_in, product_id=unique_product.id,
                ),
                uow=uow,
            )
            await invalidate_products_cache()
            return ReadAbsoluteProductSchema(
                **unique_product.model_dump(),
                images=new_images,
                variations=product_variations,
            )
