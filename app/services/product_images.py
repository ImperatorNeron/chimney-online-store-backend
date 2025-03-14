from abc import ABC, abstractmethod

from app.schemas.product_images import ProductImageCreate
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductImageService(ABC):

    @abstractmethod
    async def bulk_add(
        self,
        images: list[ProductImageCreate],
        uow: AbstractUnitOfWork,
    ) -> None: ...


class ProductImageService(AbstractProductImageService):

    async def bulk_add(
        self,
        images: list[ProductImageCreate],
        uow: AbstractUnitOfWork,
    ) -> None:
        await uow.products_images.bulk_add(images=images)
