from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import ProductCreationException
from app.schemas.product_images import CreateProductImageSchema
from app.schemas.products import CreateProductSchema, ReadFullProductSchema
from app.services.files import AbstractFileUploadService
from app.services.product_images import AbstractProductImageService
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_in: CreateProductSchema,
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema: ...


@dataclass
class CreateProductUseCase(AbstractCreateProductUseCase):

    product_service: AbstractProductService
    product_image_service: AbstractProductImageService
    file_service: AbstractFileUploadService

    async def execute(
        self,
        product_in: CreateProductSchema,
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema:
        image_data = []
        try:
            async with uow:

                product = await self.product_service.create(
                    product_in=product_in,
                    uow=uow,
                )

                for img in images:
                    await self.file_service.verify_file(img)
                    metadata = self.file_service.get_metadata(img)
                    await self.file_service.bwrite_file(img, metadata["path"])
                    image_data.append(
                        CreateProductImageSchema(
                            file_path=metadata["path"],
                            alt=product.name,
                            product_id=product.id,
                        ),
                    )

                return ReadFullProductSchema(
                    **product.model_dump(),
                    images=await self.product_image_service.bulk_create(
                        images=image_data,
                        uow=uow,
                    ),
                )
        except BaseAppException:
            await self.file_service.cleanup_files(image_data)
            raise
        except Exception:
            await self.file_service.cleanup_files(image_data)
            raise ProductCreationException()
