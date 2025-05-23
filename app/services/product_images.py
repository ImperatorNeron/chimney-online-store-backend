from abc import ABC, abstractmethod

from app.core.exceptions.common import ForeignKeyConstraintViolationException
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductImageService(ABC):

    @abstractmethod
    async def get_images(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]: ...

    @abstractmethod
    async def bulk_create(
        self,
        images: list[CreateProductImageSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]: ...

    @abstractmethod
    async def delete_by_ids(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> None: ...


class ProductImageService(AbstractProductImageService):

    async def get_images(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]:
        if not await uow.unique_products.exists(id=product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
        return await uow.products_images.all(filters={"product_id": product_id})

    async def bulk_create(
        self,
        images: list[CreateProductImageSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]:
        return await uow.products_images.bulk_create(data_list=images)

    async def delete_by_ids(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> None:
        return await uow.products_images.delete_by_ids(ids=ids)
