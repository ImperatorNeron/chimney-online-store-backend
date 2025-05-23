from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import ReadAbsoluteProductSchema
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

    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadAbsoluteProductSchema:
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
            return ReadAbsoluteProductSchema(
                **unique_product.model_dump(),
                images=images,
                variations=variations,
            )
