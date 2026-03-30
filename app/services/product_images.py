from abc import abstractmethod
from typing import Type

from app.core.exceptions.common import ForeignKeyConstraintViolationException
from app.mappers.products import ProductImageCreateMapper, ProductImageReadMapper
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.services.base import AbstractRead, Read
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductImageService(AbstractRead[ReadProductImageSchema]):

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


class ProductImageService(AbstractProductImageService, Read[ReadProductImageSchema]):

    repository_name: str = "products_images"
    read_mapper: Type[ProductImageReadMapper] = ProductImageReadMapper
    create_mapper: Type[ProductImageCreateMapper] = ProductImageCreateMapper

    async def list_all(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]:
        if not await uow.unique_products.exists(id=product_id):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
        return await super().list_all(uow=uow, filters={"product_id": product_id})

    async def bulk_create(
        self,
        images: list[CreateProductImageSchema],
        uow: AbstractUnitOfWork,
    ) -> list[ReadProductImageSchema]:
        return self.read_mapper.to_dto_list(
            await uow.products_images.bulk_create(
                data_list=self.create_mapper.to_model_list(images)
            )
        )

    async def delete_by_ids(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> None:
        if ids:
            return await uow.products_images.delete(id__in=ids)
