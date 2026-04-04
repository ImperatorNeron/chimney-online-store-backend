import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import UploadFile

from app.mappers.products import (
    ProductVariationToBaseProductVariationUpdateMapper,
    ProductVariationToFullProductVariationUpdateMapper,
)
from app.schemas.products import (
    ReadAbsoluteProductSchema,
    UpdateUniqueProductSchema,
    UpdateVariationSchema,
    VariationAction,
)
from app.services.files import AbstractFileStorageService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.services.unique_products import AbstractUniqueProductService
from app.use_cases.products._shared import invalidate_products_cache, upload_and_create_product_images
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractUpdateProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_id: int,
        product_in: UpdateUniqueProductSchema,
        images: list[UploadFile],
        delete_images_ids: list[int],
        variations: list[UpdateVariationSchema],
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema: ...


@dataclass
class UpdateProductUseCase(AbstractUpdateProductUseCase):
    product_service: AbstractProductService
    unique_product_service: AbstractUniqueProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileStorageService

    async def execute(
        self,
        product_id: int,
        product_in: UpdateUniqueProductSchema,
        images: list[UploadFile],
        delete_images_ids: list[int],
        variations: list[UpdateVariationSchema],
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema:
        async with uow:
            updated_unique_product = await self.unique_product_service.update(
                item_id=product_id,
                item_in=product_in,
                uow=uow,
            )
            if delete_images_ids:
                await self.product_image_service.bulk_delete(
                    id__in=delete_images_ids,
                    uow=uow,
                )

            new_images = await upload_and_create_product_images(
                images=images,
                product_id=product_id,
                product_slug=updated_unique_product.slug,
                alt=updated_unique_product.name,
                file_service=self.file_service,
                product_image_service=self.product_image_service,
                uow=uow,
                logger=logger,
                log_error_message="Failed to update product: %s",
            )

            new_variations = []

            for variation in variations:
                match variation.action:
                    case VariationAction.create:
                        new_variation = await self.product_service.bulk_create(
                            items_in=[
                                ProductVariationToFullProductVariationUpdateMapper.to_dto(
                                    variation, product_id=product_id,
                                ),
                            ],
                            uow=uow,
                        )

                        new_variations.append(new_variation[0])
                    case VariationAction.update:
                        new_variations.append(
                            await self.product_service.update(
                                item_id=variation.id,
                                item_in=ProductVariationToBaseProductVariationUpdateMapper.to_dto(
                                    variation,
                                ),
                                uow=uow,
                            ),
                        )
                    case VariationAction.delete:
                        await self.product_service.delete(
                            id=variation.id,
                            uow=uow,
                        )

            product_key = (
                f"product:{hashlib.sha256(product_in.slug.encode()).hexdigest()}"
            )
            await invalidate_products_cache(extra_keys=[product_key])

            return ReadAbsoluteProductSchema(
                **updated_unique_product.model_dump(),
                images=new_images,
                variations=new_variations,
            )
