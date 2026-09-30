from typing import Type

from app.core.exceptions.common import ForeignKeyConstraintViolationException
from app.mappers.products import ProductImageCreateMapper, ProductImageReadMapper
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.services.base import AbstractCreate, AbstractDelete, AbstractRead, Create, Delete, Read
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductImageService(
    AbstractRead[ReadProductImageSchema],
    AbstractCreate[ReadProductImageSchema, CreateProductImageSchema],
    AbstractDelete,
):
    pass


class ProductImageService(
    AbstractProductImageService,
    Read[ReadProductImageSchema],
    Create[ReadProductImageSchema, CreateProductImageSchema],
    Delete,
):
    repository_name: str = "products_images"
    read_mapper: Type[ProductImageReadMapper] = ProductImageReadMapper
    create_mapper: Type[ProductImageCreateMapper] = ProductImageCreateMapper
    read_create_mapper: Type[ProductImageReadMapper] = ProductImageReadMapper

    async def _validate_list_all(self, uow: AbstractUnitOfWork, filters: dict, **kwargs):
        if not await uow.unique_products.exists(id=filters.get("product_id")):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
