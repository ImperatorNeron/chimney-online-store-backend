from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import ProductCreationException
from app.schemas.product_images import CreateProductImageSchema
from app.schemas.products import ReadUniqueProductSchema, UpdateUniqueProductSchema
from app.services.files import AbstractFileUploadService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateUniqueProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        unique_product_id: int,
        deleted_images_ids: list[int],
        product_in: UpdateUniqueProductSchema,
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadUniqueProductSchema: ...


@dataclass
class UpdateUniqueProductUseCase(AbstractUpdateUniqueProductUseCase):

    product_service: AbstractProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileUploadService

    async def execute(
        self,
        unique_product_id: int,
        deleted_images_ids: list[int],
        product_in: UpdateUniqueProductSchema,
        uow: AbstractUnitOfWork,
        images: list = None,
    ) -> ReadUniqueProductSchema:
        async with uow:
            image_data = []

            unique_product = await self.product_service.update_unique(
                unique_product_id=unique_product_id,
                product_in=product_in,
                uow=uow,
            )

            await self.product_image_service.delete_by_ids(ids=deleted_images_ids, uow=uow)

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
                await self.product_image_service.bulk_create(
                    images=image_data,
                    uow=uow,
                )
            except BaseAppException:
                await self.file_service.cleanup_files(image_data)
                raise
            except Exception:
                await self.file_service.cleanup_files(image_data)
                raise ProductCreationException()

            return unique_product
