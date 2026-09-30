from typing import Type

from app.core.exceptions.common import (
    ForeignKeyConstraintViolationException,
    ItemNotFoundException,
    UniqueConstraintViolationsException,
)
from app.mappers.products import (
    FullUniqueProductReadMapper,
    UniqueProductCreateMapper,
    UniqueProductReadMapper,
    UniqueProductUpdateMapper,
)
from app.schemas.products import CreateUniqueProductSchema, ReadUniqueProductSchema
from app.services.base import AbstractCRUDService, CRUDService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUniqueProductService(
    AbstractCRUDService[
        ReadUniqueProductSchema,
        CreateUniqueProductSchema,
        CreateUniqueProductSchema,
    ],
):
    pass


class UniqueProductService(
    AbstractUniqueProductService,
    CRUDService[
        ReadUniqueProductSchema,
        CreateUniqueProductSchema,
        CreateUniqueProductSchema,
    ],
):
    repository_name: str = "unique_products"
    read_mapper: Type[FullUniqueProductReadMapper] = FullUniqueProductReadMapper
    create_mapper: Type[UniqueProductCreateMapper] = UniqueProductCreateMapper
    update_mapper: Type[UniqueProductUpdateMapper] = UniqueProductUpdateMapper
    read_create_mapper: Type[UniqueProductReadMapper] = UniqueProductReadMapper
    read_update_mapper: Type[UniqueProductReadMapper] = UniqueProductReadMapper

    async def get_one(
        self,
        uow: AbstractUnitOfWork,
        conditions: dict,
    ) -> ReadUniqueProductSchema:
        slug = conditions.get("slug")
        id_ = conditions.get("id")
        if slug and not await uow.unique_products.exists(slug=conditions.get("slug")):
            raise ItemNotFoundException(
                {"slug": "Продукт з цим url не існує."},
                detail="Не існує продукту з даним slug",
            )
        if id_ and not await uow.unique_products.exists(id=id_):
            raise ForeignKeyConstraintViolationException(
                {"product_id": "Продукту не існує."},
                detail="Не існує даного продукту",
            )
        # We use this mapper, just to not write full name here
        return self.read_create_mapper.to_dto(await uow.unique_products.get(**conditions))

    async def _create_validation(
        self,
        *args,
        uow: AbstractUnitOfWork,
        item_in: CreateUniqueProductSchema,
        **kwargs,
    ):
        if await uow.unique_products.exists(slug=item_in.slug):
            raise UniqueConstraintViolationsException(
                {"slug": "Продукт з цим url вже існує."},
                detail="Продукт з цим slug вже існує",
            )
        if not await uow.categories.exists(id=item_in.category_id):
            raise ForeignKeyConstraintViolationException(
                {"category_id": "Категорія не існує."},
                detail="Не існує даної категорії",
            )
