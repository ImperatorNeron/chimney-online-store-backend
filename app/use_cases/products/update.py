import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import UploadFile
from fastapi_cache import FastAPICache

from app.core.constants import CACHED_PRODUCT_KEYS
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import ProductCreationException
from app.schemas.product_images import CreateProductImageSchema
from app.schemas.products import (
    ReadAbsoluteProductSchema,
    UpdateUniqueProductSchema,
    UpdateVariationSchema,
    VariationAction,
)
from app.services.files import AbstractFileUploadService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


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
    product_image_service: AbstractProductImageService
    file_service: AbstractFileUploadService

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
            updated_unique_product = await self.product_service.update_unique(
                unique_product_id=product_id,
                product_in=product_in,
                uow=uow,
            )

            await self.product_image_service.delete_by_ids(
                ids=delete_images_ids,
                uow=uow,
            )

            created_images = []
            for img in images:
                await self.file_service.verify_file(img)
                meta = self.file_service.get_metadata(img)
                await self.file_service.bwrite_file(img, meta["path"])
                created_images.append(
                    CreateProductImageSchema(
                        file_path=meta["path"],
                        alt=updated_unique_product.name,
                        product_id=product_id,
                    ),
                )
            if created_images:
                new_imgs = await self.product_image_service.bulk_create(
                    images=created_images,
                    uow=uow,
                )
            else:
                new_imgs = []

            new_variations = []
            for var in variations:
                if var.action == VariationAction.create:
                    new_variation = await self.product_service.create_variations(
                        unique_product_id=product_id,
                        products_in=[var],
                        uow=uow,
                    )
                    new_variations.append(new_variation[0])
                elif var.action == VariationAction.update:
                    current_variation = await self.product_service.get_variation(
                        variation_id=var.id,
                        uow=uow,
                    )
                    new_variations.append(
                        await self.product_service.update_variation(
                            variation_id=var.id,
                            product_in=var,
                            uow=uow,
                            static_discount=(
                                0 if current_variation.price == var.price else 30
                            ),
                        ),
                    )
                elif var.action == VariationAction.delete:
                    await self.product_service.delete_variation(
                        product_variation_id=var.id,
                        uow=uow,
                    )
            for key in CACHED_PRODUCT_KEYS:
                await FastAPICache.get_backend().set(key, None, expire=1)

            CACHED_PRODUCT_KEYS.clear()

            product_key = (
                f"product:{hashlib.sha256(product_in.slug.encode()).hexdigest()}"
            )
            await FastAPICache.get_backend().set(product_key, None, expire=1)

            return ReadAbsoluteProductSchema(
                **updated_unique_product.model_dump(),
                images=new_imgs,
                variations=new_variations,
            )


@dataclass
class UpdateProductWithSupabaseUseCase(AbstractUpdateProductUseCase):
    product_service: AbstractProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileUploadService

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
            updated_unique_product = await self.product_service.update_unique(
                unique_product_id=product_id,
                product_in=product_in,
                uow=uow,
            )

            await self.product_image_service.delete_by_ids(
                ids=delete_images_ids,
                uow=uow,
            )

            created_images = []
            try:
                for img in images:
                    await self.file_service.verify_file(img)
                    path = await self.file_service.write_to_supabase(
                        file=img,
                        unique_product_slug=product_in.slug,
                    )
                    created_images.append(
                        CreateProductImageSchema(
                            file_path=path,
                            alt=product_in.name,
                            product_id=product_id,
                        ),
                    )
                if created_images:
                    new_imgs = await self.product_image_service.bulk_create(
                        images=created_images,
                        uow=uow,
                    )
                else:
                    new_imgs = []

            except BaseAppException:
                await self.file_service.delete_from_supabase(created_images)
                raise
            except Exception:
                await self.file_service.delete_from_supabase(created_images)
                raise ProductCreationException()

            new_variations = []
            for var in variations:
                if var.action == VariationAction.create:
                    new_variation = await self.product_service.create_variations(
                        unique_product_id=product_id,
                        products_in=[var],
                        uow=uow,
                    )
                    new_variations.append(new_variation[0])
                elif var.action == VariationAction.update:
                    current_variation = await self.product_service.get_variation(
                        variation_id=var.id,
                        uow=uow,
                    )
                    new_variations.append(
                        await self.product_service.update_variation(
                            variation_id=var.id,
                            product_in=var,
                            uow=uow,
                            static_discount=(
                                0 if current_variation.price == var.price else 30
                            ),
                        ),
                    )
                elif var.action == VariationAction.delete:
                    await self.product_service.delete_variation(
                        product_variation_id=var.id,
                        uow=uow,
                    )
            for key in CACHED_PRODUCT_KEYS:
                await FastAPICache.get_backend().set(key, None, expire=1)

            CACHED_PRODUCT_KEYS.clear()

            product_key = (
                f"product:{hashlib.sha256(product_in.slug.encode()).hexdigest()}"
            )
            await FastAPICache.get_backend().set(product_key, None, expire=1)

            return ReadAbsoluteProductSchema(
                **updated_unique_product.model_dump(),
                images=new_imgs,
                variations=new_variations,
            )
