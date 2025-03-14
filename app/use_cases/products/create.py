from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import CreateProductSchema, ReadFullProductSchema
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

    async def execute(
        self,
        product_in: CreateProductSchema,
        images: list,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema:
        async with uow:
            product = await self.product_service.create(
                product_in=product_in,
                uow=uow,
            )

            # TODO: create fileservice and cover it in schema
            image_data = []
            for img in images:
                image_data.append(
                    {
                        "file_path": img.filename,
                        "product_id": product.id,
                        "alt": product.name,
                    },
                )

            await self.product_image_service.bulk_add(images=image_data, uow=uow)
            return ReadFullProductSchema(**product.model_dump(), images=[])
