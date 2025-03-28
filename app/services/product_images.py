from abc import ABC, abstractmethod

from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductImageService(ABC):

    @abstractmethod
    async def bulk_create(
        self,
        images: list[CreateProductImageSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]: ...


class ProductImageService(AbstractProductImageService):

    async def bulk_create(
        self,
        images: list[CreateProductImageSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]:
        return await uow.products_images.bulk_create(data_list=images)
